import streamlit as st
import requests

st.set_page_config(page_title="MoodMate Pro", layout="wide")

# STYLING: Light Background with Dark Navy Text for perfect visibility
st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; }
    h1, h2, h3, p, span, label { color: #1e3a8a !important; font-weight: bold; }
    .stButton>button { background-color: #1e3a8a; color: white; border-radius: 10px; height: 3em; width: 100%; }
    .song-card { 
        background-color: white; 
        padding: 20px; 
        border-radius: 15px; 
        border: 2px solid #1e3a8a; 
        margin-bottom: 15px;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.1);
    }
    .song-card h4 { color: #1e3a8a !important; margin: 0; }
    .song-card p { color: #4b5563 !important; margin: 5px 0; }
    .song-card a { color: #1db954 !important; text-decoration: none; font-size: 18px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎵 MoodMate: Music Recommender")
st.write("Analyze your mood via Text, Camera, or Photo Upload.")

tab1, tab2, tab3 = st.tabs(["📝 Text Analysis", "📸 Live Camera", "📁 Upload Photo"])

def display_results(emotion, songs):
    st.markdown(f"## Your Emotion: <span style='color:#ef4444'>{emotion}</span>", unsafe_allow_html=True)
    st.write("### Recommended Tracks for you:")
    
    for s in songs:
        st.markdown(f"""
            <div class="song-card">
                <h4>{s['title']}</h4>
                <p>By {s['artist']}</p>
                <a href="{s['url']}" target="_blank">▶ Play on Spotify</a>
            </div>
        """, unsafe_allow_html=True)

# --- TEXT TAB ---
with tab1:
    user_input = st.text_input("Type how you are feeling:", placeholder="e.g. I am feeling very happy today!")
    if st.button("Analyze Mood & Get Songs"):
        if user_input:
            res = requests.post("http://127.0.0.1:8000/predict_text", json={"text": user_input})
            if res.status_code == 200:
                data = res.json()
                display_results(data['emotion'], data['songs'])

# --- CAMERA TAB ---
with tab2:
    cam_img = st.camera_input("Capture your face")
    if cam_img:
        res = requests.post("http://127.0.0.1:8000/predict", files={"file": cam_img.getvalue()})
        if res.status_code == 200:
            data = res.json()
            display_results(data['emotion'], data['songs'])

# --- UPLOAD TAB ---
with tab3:
    up_img = st.file_uploader("Upload a selfie")
    if up_img:
        res = requests.post("http://127.0.0.1:8000/predict", files={"file": up_img.getvalue()})
        if res.status_code == 200:
            data = res.json()
            display_results(data['emotion'], data['songs'])