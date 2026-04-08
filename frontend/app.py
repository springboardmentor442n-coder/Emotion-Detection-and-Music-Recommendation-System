import base64
import os
import time

import cv2
import numpy as np
import requests
import streamlit as st
import streamlit.components.v1

# =========================
# Config
# =========================
FLASK_URL = os.getenv("FLASK_URL", "http://localhost:5000")  # Change if Flask server is hosted elsewhere

st.set_page_config(
    page_title="MoodMate 🎵",
    page_icon="🎵",
    layout="wide"
)

# =========================
# Custom Styling
# =========================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(160deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    color: #eaeaea;
}
section[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.05);
    border-right: 1px solid rgba(255,255,255,0.1);
}
.mood-card {
    background: linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03));
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 16px;
    padding: 16px 20px;
    margin-bottom: 12px;
}
.emotion-badge {
    display: inline-block;
    padding: 6px 18px;
    border-radius: 20px;
    font-size: 1.1rem;
    font-weight: 700;
    margin: 10px 0;
}
.badge-happy    { background: #f9ca24; color: #1a1a2e; }
.badge-sad      { background: #6c5ce7; color: white; }
.badge-angry    { background: #e17055; color: white; }
.badge-fear     { background: #636e72; color: white; }
.badge-surprise { background: #fd79a8; color: white; }
.badge-neutral  { background: #00b894; color: white; }
.stButton > button {
    background: linear-gradient(135deg, #6c5ce7, #a29bfe);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 10px 24px;
    font-weight: 600;
    font-size: 1rem;
    width: 100%;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #a29bfe, #6c5ce7);
}
h1, h2, h3 { color: #ffffff !important; }
p, label   { color: #cccccc !important; }
.divider {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.1);
    margin: 20px 0;
}
</style>
""", unsafe_allow_html=True)

# =========================
# Session State
# =========================
for key, default in [
    ("emotion", None),
    ("songs", []),
    ("webcam_emotion", None),
    ("webcam_confidence", 0.0),
    # shared dict for the background detection thread to write results into
    ("detect_result", {"emotion": None, "confidence": 0.0, "songs": [], "pending": False, "error": None}),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# =========================
# Helpers
# =========================
EMOTION_EMOJI = {
    "happy": "😊", "sad": "😢", "angry": "😠",
    "fear": "😨", "surprise": "😲", "neutral": "😐"
}


def emotion_badge(emotion: str) -> str:
    if not emotion:
        return ""
    e = emotion.lower()
    emoji = EMOTION_EMOJI.get(e, "🎭")
    return f'<div class="emotion-badge badge-{e}">{emoji} {emotion.capitalize()}</div>'


def render_songs(songs: list):
    if not songs:
        st.info("No songs found.")
        return
    for song in songs:
        name    = song.get("name",   "Unknown Title")
        artist  = song.get("artist", "Unknown Artist")
        yt_embed  = song.get("youtube_embed_url")   # e.g. https://www.youtube.com/embed/XXXX
        yt_search = song.get("youtube_link", "")    # always-valid search URL
        sp_preview = song.get("spotify_preview")    # 30s mp3 or None
        sp_link    = song.get("spotify_link", "")   # Spotify page or search

        # ── Song card header ──────────────────────────────────────
        st.markdown(
            f'''<div class="mood-card">
  🎵 <strong style="font-size:1.05rem;">{name}</strong>
  <br><span style="color:#a29bfe;font-size:0.9rem;">🎤 {artist}</span>
  <br>
  <a href="{yt_search}" target="_blank"
     style="color:#ff6b6b;font-size:0.82rem;margin-right:12px;">&#9654; YouTube</a>
  <a href="{sp_link}" target="_blank"
     style="color:#1db954;font-size:0.82rem;">🎶 Spotify</a>
</div>''',
            unsafe_allow_html=True
        )

        # ── Spotify 30s preview (audio tag — no iframe needed) ────
        if sp_preview:
            st.audio(sp_preview, format="audio/mp3")

        # ── YouTube embed (full player) ───────────────────────────
        elif yt_embed:
            st.components.v1.iframe(
                yt_embed + "?rel=0&modestbranding=1",
                height=220
            )

        st.markdown("<div style='margin-bottom:4px'></div>", unsafe_allow_html=True)


def get_songs(emotion: str, uplift: bool) -> list:
    try:
        r = requests.post(
            f"{FLASK_URL}/text",
            json={"text": emotion, "uplift": uplift},
            timeout=60
        )
        r.raise_for_status()
        return r.json().get("songs", [])
    except Exception as e:
        st.error(f"Backend error: {e}")
        return []


def get_text_emotion(text: str):
    try:
        r = requests.post(
            f"{FLASK_URL}/text",
            json={"text": text, "uplift": False},
            timeout=60
        )
        r.raise_for_status()
        data = r.json()
        return data.get("emotion"), data.get("songs", [])
    except Exception as e:
        st.error(f"Backend error: {e}")
        return None, []


def get_image_emotion(image_bytes: bytes, uplift: bool = False):
    try:
        files = {"file": ("photo.jpg", image_bytes, "image/jpeg")}
        data  = {"uplift": str(uplift).lower()}
        resp  = requests.post(f"{FLASK_URL}/upload", files=files, data=data, timeout=60)
        resp.raise_for_status()
        result = resp.json()
        return result.get("emotion"), result.get("songs", [])
    except Exception as e:
        st.error(f"Image upload error: {e}")
        return None, []


def get_webcam_frame_emotion(frame, uplift=False):
    """Synchronous: encode frame, POST to /detect-face, return (emotion, confidence, songs)."""
    try:
        small   = cv2.resize(frame, (320, 240))
        ok, buf = cv2.imencode(".jpg", small, [cv2.IMWRITE_JPEG_QUALITY, 80])
        if not ok:
            return None, 0.0, []
        b64 = base64.b64encode(buf.tobytes()).decode("utf-8")
        resp = requests.post(
            f"{FLASK_URL}/detect-face",
            json={"image": b64, "uplift": uplift},
            timeout=30
        )
        resp.raise_for_status()
        d = resp.json()
        return d.get("emotion"), d.get("confidence", 0.0), d.get("songs", [])
    except Exception as e:
        return None, 0.0, []


# =========================
# Header
# =========================
st.markdown("# 🎵 MoodMate")
st.markdown("##### *Music that matches — or lifts — your mood*")
st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# =========================
# Sidebar
# =========================
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    uplift = st.toggle(
        "🚀 Uplift my mood", value=False,
        help="ON = happy songs to cheer you up | OFF = match your mood"
    )
    st.markdown("---")
    st.markdown("**How it works:**")
    st.markdown("1. Choose an input method")
    st.markdown("2. We detect your emotion")
    st.markdown("3. Get song recommendations")
    st.markdown("---")
    if st.session_state.emotion:
        st.markdown("**Last detected:**")
        st.markdown(emotion_badge(st.session_state.emotion), unsafe_allow_html=True)

# =========================
# Tabs
# =========================
tab_text, tab_upload, tab_webcam = st.tabs([
    "💬 Text", "🖼️ Upload Photo", "📷 Live Webcam"
])

# -------------------------
# Tab 1: Text
# -------------------------
with tab_text:
    st.markdown("### 💬 How are you feeling?")
    user_text = st.text_area(
        "Describe your mood:",
        placeholder="e.g. I'm feeling anxious about my exam tomorrow...",
        height=120,
        label_visibility="collapsed"
    )
    if st.button("🎵 Get My Playlist", key="btn_text"):
        if not user_text.strip():
            st.warning("Please type something first!")
        else:
            with st.spinner("Analyzing your mood..."):
                emotion, songs = get_text_emotion(user_text)
                if emotion:
                    st.session_state.emotion = emotion
                    st.session_state.songs   = songs
                    st.markdown(emotion_badge(emotion), unsafe_allow_html=True)
                    if uplift:
                        songs = get_songs(emotion, uplift=True)
                    render_songs(songs)

# -------------------------
# Tab 2: Upload Photo
# -------------------------
with tab_upload:
    st.markdown("### 🖼️ Upload a face photo")
    uploaded = st.file_uploader(
        "Choose an image",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed"
    )
    if uploaded:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(uploaded, caption="Your photo", width="stretch")
        with col2:
            if st.button("🎵 Detect & Recommend", key="btn_upload"):
                with st.spinner("Detecting emotion from face..."):
                    emotion, songs = get_image_emotion(uploaded.read(), uplift=uplift)
                    if emotion:
                        st.session_state.emotion = emotion
                        st.session_state.songs   = songs
                        st.markdown(emotion_badge(emotion), unsafe_allow_html=True)
                        render_songs(songs)
                    else:
                        st.error("Could not detect emotion. Try a clearer photo.")

# -------------------------
# Tab 3: Live Webcam
# -------------------------
with tab_webcam:
    st.markdown("### 📷 Real-time Emotion Detection")
    st.markdown("Face is scanned every **5 seconds**. Songs appear below the feed.")

    run_webcam = st.checkbox("🎥 Start Webcam", value=False)

    frame_placeholder  = st.empty()
    status_placeholder = st.empty()

    if run_webcam:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            st.error("Could not open webcam. Check permissions.")
        else:
            stop             = st.button("⏹ Stop Webcam", key="stop_webcam")
            # Persistent placeholders for emotion badge + songs — created ONCE outside loop
            emotion_ph = st.empty()
            songs_ph   = st.empty()

            last_detect_time = 0
            detect_interval  = 5

            while not stop:
                ret, frame = cap.read()
                if not ret:
                    st.error("Failed to read from webcam.")
                    break

                # Show live feed
                frame_placeholder.image(
                    cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
                    channels="RGB", width="stretch"
                )

                now = time.time()
                if now - last_detect_time >= detect_interval:
                    last_detect_time = now
                    status_placeholder.info("🔍 Detecting emotion…")

                    emotion, confidence, songs = get_webcam_frame_emotion(frame.copy(), uplift)

                    if emotion:
                        # Save to session state
                        st.session_state.webcam_emotion = emotion.lower()
                        st.session_state.emotion        = emotion.lower()
                        st.session_state.songs          = songs

                        status_placeholder.empty()

                        # Update badge — single markdown fits in st.empty()
                        emotion_ph.markdown(
                            emotion_badge(emotion)
                            + f' <span style="font-size:0.85rem;color:#aaa;">({confidence:.0%})</span>',
                            unsafe_allow_html=True
                        )

                        # FIX: songs_ph.empty() is ONE slot — use a WITH block to
                        # put a container inside it, then write all songs into that container
                        with songs_ph.container():
                            render_songs(songs)
                    else:
                        status_placeholder.warning("🤷 No face detected — move closer or improve lighting.")

                time.sleep(0.05)

            cap.release()
            frame_placeholder.empty()
            status_placeholder.empty()
            st.success("Webcam stopped.")

    # Always show last result below (survives stop / page interactions)
    if st.session_state.get("webcam_emotion"):
        st.markdown("**Last detected:**")
        st.markdown(emotion_badge(st.session_state.webcam_emotion), unsafe_allow_html=True)
        render_songs(st.session_state.get("songs", []))