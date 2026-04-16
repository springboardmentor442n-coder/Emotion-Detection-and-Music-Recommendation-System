"""
app.py  —  MoodMate v3  (Redesigned Dashboard)
───────────────────────────────────────────────
New in v3:
  • Fully redesigned dark dashboard UI
  • Emotion confidence bar chart (Chart.js)
  • Training accuracy / loss graph (served from models/ folder)
  • Live audio player — plays Spotify preview when emotion detected
  • Song cards with play button, artist, genre, Spotify link
  • Webcam live feed with face box overlay
  • Analysis section — emotion stats per session
"""

import os, sys, gc, base64, uuid, json
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from flask import Flask, request, jsonify, render_template_string, send_from_directory
from flask_cors import CORS
from src.emotion_predictor import predict_from_path, predict_from_array
from src.music_recommender  import MusicRecommender
from src.emotion_mapping    import get_emotion_info
from utils.helper_functions import (
    detect_faces, crop_face, draw_face_box,
    image_to_base64, emotion_emoji, logger
)

app  = Flask(__name__)
CORS(app)

recommender   = MusicRecommender(csv_path=os.path.join(BASE_DIR, "data", "music_data.csv"))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ──────────────────────────────────────────────────────────────────────────────
# SERVE TRAINING CURVE IMAGE
# ──────────────────────────────────────────────────────────────────────────────
@app.route("/models/<path:filename>")
def serve_model_file(filename):
    models_dir = os.path.join(BASE_DIR, "models")
    return send_from_directory(models_dir, filename)


# ──────────────────────────────────────────────────────────────────────────────
# HTML DASHBOARD
# ──────────────────────────────────────────────────────────────────────────────
INDEX_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>MoodMate — Emotion Music Dashboard</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0d0d14;--surface:#13131f;--card:#1a1a2e;--border:#ffffff14;
  --accent:#7c4dff;--accent2:#e040fb;--green:#00e5aa;--text:#e8e8f0;
  --muted:#6b6b8a;--danger:#ff5c5c;--warn:#ffb347;
}
body{background:var(--bg);color:var(--text);font-family:'Segoe UI',system-ui,sans-serif;min-height:100vh}

/* ── SIDEBAR ── */
.sidebar{
  position:fixed;top:0;left:0;width:220px;height:100vh;
  background:var(--surface);border-right:1px solid var(--border);
  display:flex;flex-direction:column;padding:1.5rem 0;z-index:100
}
.logo{padding:0 1.5rem 1.5rem;border-bottom:1px solid var(--border)}
.logo h1{font-size:1.3rem;background:linear-gradient(135deg,var(--accent),var(--accent2));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:700}
.logo p{font-size:.75rem;color:var(--muted);margin-top:.2rem}
.nav{padding:1rem 0;flex:1}
.nav-item{
  display:flex;align-items:center;gap:.75rem;padding:.7rem 1.5rem;
  cursor:pointer;color:var(--muted);font-size:.88rem;transition:all .15s;
  border-left:3px solid transparent
}
.nav-item:hover{color:var(--text);background:#ffffff08}
.nav-item.active{color:var(--accent);background:#7c4dff18;border-left-color:var(--accent)}
.nav-icon{font-size:1.1rem;width:20px;text-align:center}
.sidebar-footer{padding:1rem 1.5rem;border-top:1px solid var(--border);font-size:.75rem;color:var(--muted)}

/* ── MAIN ── */
.main{margin-left:220px;padding:2rem;min-height:100vh}
.page{display:none}.page.active{display:block}
.page-title{font-size:1.4rem;font-weight:600;margin-bottom:1.5rem;color:var(--text)}

/* ── GRID ── */
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:1.25rem}
.grid-3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:1rem}
.grid-4{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem}

/* ── CARDS ── */
.card{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:1.5rem}
.card-sm{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:1rem}
.card-title{font-size:.8rem;color:var(--muted);text-transform:uppercase;letter-spacing:.06em;margin-bottom:.5rem}
.stat-value{font-size:1.8rem;font-weight:700;color:var(--text)}
.stat-sub{font-size:.78rem;color:var(--muted);margin-top:.25rem}

/* ── UPLOAD ZONE ── */
.upload-zone{
  border:2px dashed var(--accent);border-radius:12px;padding:2.5rem;
  text-align:center;cursor:pointer;transition:background .2s;position:relative
}
.upload-zone:hover{background:#7c4dff12}
.upload-zone input{position:absolute;inset:0;opacity:0;cursor:pointer;width:100%;height:100%}
.upload-icon{font-size:2.2rem;margin-bottom:.8rem}
.upload-hint{color:var(--muted);font-size:.82rem;margin-top:.4rem}
#preview-img{max-width:100%;max-height:240px;border-radius:10px;margin-top:1rem;
  display:none;border:2px solid var(--border)}

/* ── BUTTON ── */
.btn{
  display:inline-flex;align-items:center;gap:.5rem;padding:.75rem 1.5rem;
  border:none;border-radius:10px;cursor:pointer;font-size:.9rem;font-weight:600;
  transition:opacity .2s,transform .1s;width:100%;justify-content:center;margin-top:1rem
}
.btn-primary{background:linear-gradient(135deg,var(--accent),var(--accent2));color:#fff}
.btn-primary:disabled{opacity:.4;cursor:default}
.btn:active{transform:scale(.98)}
.btn-sm{width:auto;padding:.45rem .9rem;font-size:.8rem;border-radius:8px;margin-top:0}
.btn-play{background:#1DB95422;color:#1DB954;border:1px solid #1DB95455}
.btn-play:hover{background:#1DB95444}
.btn-stop{background:#ff5c5c22;color:#ff5c5c;border:1px solid #ff5c5c55}

/* ── EMOTION BADGE ── */
.emotion-result{
  display:flex;align-items:center;gap:1rem;padding:1.25rem;
  background:linear-gradient(135deg,#7c4dff18,#e040fb12);
  border:1px solid var(--accent);border-radius:12px;margin:1rem 0
}
.emotion-emoji-big{font-size:2.5rem}
.emotion-name{font-size:1.5rem;font-weight:700;text-transform:capitalize}
.emotion-conf{font-size:.85rem;color:var(--muted)}
.emotion-mood{font-size:.85rem;color:var(--accent2);margin-top:.2rem}

/* ── SONG CARDS ── */
.song-card{
  display:flex;align-items:center;gap:.75rem;padding:.85rem 1rem;
  border-radius:10px;background:#ffffff06;border:1px solid var(--border);
  margin-bottom:.6rem;transition:background .15s
}
.song-card:hover{background:#ffffff0e}
.song-num{color:var(--muted);font-size:.82rem;min-width:20px;text-align:center}
.song-info{flex:1;min-width:0}
.song-name{font-size:.9rem;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.song-meta{font-size:.77rem;color:var(--muted);margin-top:.15rem}
.song-tags{display:flex;gap:.4rem;margin-top:.35rem;flex-wrap:wrap}
.tag{font-size:.68rem;padding:.1rem .45rem;border-radius:50px}
.tag-genre{background:#7c4dff33;color:#b39dff}
.tag-val{background:#00e5aa22;color:#00e5aa}
.tag-energy{background:#ffb34722;color:#ffb347}
.song-actions{display:flex;gap:.4rem;align-items:center;flex-shrink:0}

/* ── AUDIO BAR ── */
.now-playing{
  position:fixed;bottom:0;left:220px;right:0;
  background:var(--surface);border-top:1px solid var(--border);
  padding:.75rem 2rem;display:none;align-items:center;gap:1rem;z-index:200
}
.np-info{flex:1;min-width:0}
.np-title{font-size:.88rem;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.np-artist{font-size:.76rem;color:var(--muted)}
.np-controls{display:flex;align-items:center;gap:.75rem}
.np-btn{background:none;border:1px solid var(--border);color:var(--text);
  width:34px;height:34px;border-radius:50%;cursor:pointer;font-size:.9rem;
  display:flex;align-items:center;justify-content:center;transition:background .15s}
.np-btn:hover{background:#ffffff15}
.np-btn.active{background:var(--accent);border-color:var(--accent)}
progress.np-bar{flex:1;height:4px;border-radius:2px;appearance:none;cursor:pointer}
progress.np-bar::-webkit-progress-bar{background:#ffffff22;border-radius:2px}
progress.np-bar::-webkit-progress-value{background:linear-gradient(90deg,var(--accent),var(--accent2));border-radius:2px}
.np-time{font-size:.74rem;color:var(--muted);white-space:nowrap}

/* ── WEBCAM ── */
#webcam-canvas{border-radius:12px;border:1px solid var(--border);display:block;width:100%;max-height:340px;object-fit:contain}
#webcam-status{font-size:.82rem;color:var(--muted);margin:.5rem 0;text-align:center}

/* ── CHARTS ── */
.chart-wrap{position:relative;height:220px}

/* ── CONFIDENCE BARS ── */
.conf-bar-row{display:flex;align-items:center;gap:.75rem;margin:.35rem 0}
.conf-label{font-size:.78rem;color:var(--muted);width:65px;text-align:right}
.conf-track{flex:1;height:8px;background:#ffffff12;border-radius:4px;overflow:hidden}
.conf-fill{height:100%;border-radius:4px;background:linear-gradient(90deg,var(--accent),var(--accent2));transition:width .5s ease}
.conf-pct{font-size:.75rem;color:var(--muted);width:38px}

/* ── SESSION STATS ── */
.emo-freq-bar{display:flex;align-items:center;gap:.6rem;margin:.3rem 0}
.emo-freq-label{font-size:.8rem;width:70px;color:var(--muted)}
.emo-freq-track{flex:1;height:10px;background:#ffffff10;border-radius:5px;overflow:hidden}
.emo-freq-fill{height:100%;border-radius:5px;background:var(--accent);transition:width .4s}
.emo-freq-count{font-size:.78rem;color:var(--muted);width:30px}

/* ── ERROR ── */
.error-box{background:#ff5c5c18;border:1px solid #ff5c5c55;border-radius:8px;
  padding:.7rem 1rem;color:#ff8888;font-size:.85rem;margin-top:.75rem}

/* ── SPINNER ── */
.spin{display:inline-block;width:16px;height:16px;border:2.5px solid #fff4;
  border-top-color:#fff;border-radius:50%;animation:spin .6s linear infinite;vertical-align:middle}
@keyframes spin{to{transform:rotate(360deg)}}

/* ── TRAINING GRAPH ── */
.training-img{width:100%;border-radius:10px;border:1px solid var(--border)}
.no-model-msg{text-align:center;padding:2rem;color:var(--muted);font-size:.88rem}

/* ── SCROLLBAR ── */
::-webkit-scrollbar{width:6px;height:6px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:#ffffff22;border-radius:3px}

@media(max-width:900px){
  .sidebar{width:60px}.sidebar .logo p,.sidebar .nav-item span,.sidebar-footer{display:none}
  .logo h1{font-size:.9rem}.main{margin-left:60px}
  .grid-2,.grid-3,.grid-4{grid-template-columns:1fr}
  .now-playing{left:60px}
}
</style>
</head>
<body>

<!-- ═══ SIDEBAR ═══════════════════════════════════════════════════════════ -->
<nav class="sidebar">
  <div class="logo">
    <h1>MoodMate</h1>
    <p>Emotion + Music AI</p>
  </div>
  <div class="nav">
    <div class="nav-item active" onclick="showPage('detect')">
      <span class="nav-icon">🎭</span><span>Detect</span>
    </div>
    <div class="nav-item" onclick="showPage('webcam')">
      <span class="nav-icon">🎥</span><span>Webcam</span>
    </div>
    <div class="nav-item" onclick="showPage('analysis')">
      <span class="nav-icon">📊</span><span>Analysis</span>
    </div>
    <div class="nav-item" onclick="showPage('training')">
      <span class="nav-icon">🧠</span><span>Training</span>
    </div>
  </div>
  <div class="sidebar-footer">MoodMate v3 · 50k songs</div>
</nav>

<!-- ═══ MAIN CONTENT ══════════════════════════════════════════════════════ -->
<main class="main" id="main-content">

<!-- ── PAGE: DETECT ──────────────────────────────────────────────────────── -->
<div class="page active" id="page-detect">
  <p class="page-title">Emotion Detection</p>
  <div class="grid-2" style="align-items:start">

    <!-- Left: Upload -->
    <div>
      <div class="card">
        <div class="card-title">Upload Face Image</div>
        <div class="upload-zone" id="drop-zone">
          <input type="file" id="fileInput" accept="image/*" onchange="onFileSelected(event)"/>
          <div class="upload-icon">📸</div>
          <p>Click or drag &amp; drop a photo</p>
          <p class="upload-hint">JPG · PNG · any face image</p>
        </div>
        <img id="preview-img" alt="preview"/>
        <button class="btn btn-primary" id="detectBtn" onclick="runDetection()" disabled>
          🔍 Detect Emotion &amp; Play Music
        </button>
        <div id="detect-error"></div>
      </div>

      <!-- Emotion result -->
      <div class="card" id="emotion-card" style="display:none">
        <div class="card-title">Result</div>
        <div class="emotion-result">
          <span class="emotion-emoji-big" id="res-emoji"></span>
          <div>
            <div class="emotion-name" id="res-name"></div>
            <div class="emotion-conf" id="res-conf"></div>
            <div class="emotion-mood" id="res-mood"></div>
          </div>
        </div>
        <div class="card-title" style="margin-top:1rem">All emotion scores</div>
        <div id="conf-bars"></div>
        <div class="card-title" style="margin-top:1rem">Score chart</div>
        <div class="chart-wrap"><canvas id="emotionChart"></canvas></div>
      </div>
    </div>

    <!-- Right: Songs -->
    <div>
      <div class="card" id="songs-card" style="display:none">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:1rem">
          <div class="card-title" style="margin:0">Recommended Songs</div>
          <span id="songs-emotion-badge" style="font-size:.75rem;padding:.25rem .75rem;
            border-radius:50px;background:#7c4dff33;color:#b39dff"></span>
        </div>
        <div id="song-list"></div>
      </div>
    </div>
  </div>
</div>

<!-- ── PAGE: WEBCAM ───────────────────────────────────────────────────────── -->
<div class="page" id="page-webcam">
  <p class="page-title">Live Webcam Detection</p>
  <div class="grid-2" style="align-items:start">
    <div>
      <div class="card">
        <div class="card-title">Live Feed</div>
        <video id="webcam-video" autoplay playsinline style="display:none"></video>
        <canvas id="webcam-canvas" width="520" height="360"></canvas>
        <p id="webcam-status">Click Start to activate your webcam.</p>
        <button class="btn btn-primary" id="webcamBtn" onclick="toggleWebcam()">▶ Start Webcam</button>
      </div>
      <div class="card" id="webcam-emotion-card" style="display:none;margin-top:1.25rem">
        <div class="card-title">Detected Emotion</div>
        <div class="emotion-result">
          <span class="emotion-emoji-big" id="wc-emoji"></span>
          <div>
            <div class="emotion-name" id="wc-name"></div>
            <div class="emotion-conf" id="wc-conf"></div>
            <div class="emotion-mood" id="wc-mood"></div>
          </div>
        </div>
      </div>
    </div>
    <div>
      <div class="card" id="wc-songs-card" style="display:none">
        <div class="card-title">Recommended Songs</div>
        <div id="wc-song-list"></div>
      </div>
    </div>
  </div>
</div>

<!-- ── PAGE: ANALYSIS ────────────────────────────────────────────────────── -->
<div class="page" id="page-analysis">
  <p class="page-title">Session Analysis</p>
  <div class="grid-4" style="margin-bottom:1.25rem">
    <div class="card-sm">
      <div class="card-title">Detections</div>
      <div class="stat-value" id="stat-total">0</div>
      <div class="stat-sub">This session</div>
    </div>
    <div class="card-sm">
      <div class="card-title">Top Emotion</div>
      <div class="stat-value" id="stat-top">—</div>
      <div class="stat-sub">Most frequent</div>
    </div>
    <div class="card-sm">
      <div class="card-title">Avg Confidence</div>
      <div class="stat-value" id="stat-conf">—</div>
      <div class="stat-sub">Across detections</div>
    </div>
    <div class="card-sm">
      <div class="card-title">Songs Played</div>
      <div class="stat-value" id="stat-played">0</div>
      <div class="stat-sub">This session</div>
    </div>
  </div>
  <div class="grid-2">
    <div class="card">
      <div class="card-title">Emotion Frequency</div>
      <div id="emotion-freq"></div>
    </div>
    <div class="card">
      <div class="card-title">Confidence Over Time</div>
      <div class="chart-wrap"><canvas id="timelineChart"></canvas></div>
    </div>
  </div>
  <div class="card" style="margin-top:1.25rem">
    <div class="card-title">Detection History</div>
    <div id="history-list" style="max-height:280px;overflow-y:auto"></div>
  </div>
</div>

<!-- ── PAGE: TRAINING ────────────────────────────────────────────────────── -->
<div class="page" id="page-training">
  <p class="page-title">Model Training Results</p>
  <div class="grid-3" style="margin-bottom:1.25rem">
    <div class="card-sm">
      <div class="card-title">Architecture</div>
      <div class="stat-value" style="font-size:1.1rem">MobileNetV2</div>
      <div class="stat-sub">Transfer Learning</div>
    </div>
    <div class="card-sm">
      <div class="card-title">Training Set</div>
      <div class="stat-value">28,709</div>
      <div class="stat-sub">FER-2013 images</div>
    </div>
    <div class="card-sm">
      <div class="card-title">Test Set</div>
      <div class="stat-value">3,589</div>
      <div class="stat-sub">FER-2013 images</div>
    </div>
  </div>
  <div class="grid-2">
    <div class="card">
      <div class="card-title">Training &amp; Validation Accuracy</div>
      <div id="train-acc-wrap">
        <img src="/models/training_curves_v2.png" class="training-img"
             onerror="this.style.display='none';document.getElementById('train-acc-wrap').innerHTML=noModelMsg()"
             alt="Training curves"/>
      </div>
    </div>
    <div class="card">
      <div class="card-title">Class Distribution (FER-2013 Train)</div>
      <div class="chart-wrap"><canvas id="classDistChart"></canvas></div>
    </div>
  </div>
  <div class="card" style="margin-top:1.25rem">
    <div class="card-title">Emotion Class Details</div>
    <div id="class-detail"></div>
  </div>
</div>

</main>

<!-- ═══ NOW PLAYING BAR ═══════════════════════════════════════════════════ -->
<div class="now-playing" id="now-playing">
  <div style="font-size:1.2rem">🎵</div>
  <div class="np-info">
    <div class="np-title" id="np-title">No song playing</div>
    <div class="np-artist" id="np-artist"></div>
  </div>
  <div class="np-controls">
    <button class="np-btn" id="np-prev" onclick="prevTrack()">⏮</button>
    <button class="np-btn active" id="np-play" onclick="togglePlay()">⏸</button>
    <button class="np-btn" id="np-next" onclick="nextTrack()">⏭</button>
  </div>
  <progress class="np-bar" id="np-bar" value="0" max="100"></progress>
  <span class="np-time" id="np-time">0:00 / 0:00</span>
  <button class="np-btn" onclick="stopPlayer()" title="Close">✕</button>
</div>

<audio id="audio-player"></audio>

<!-- ═══ SCRIPT ═══════════════════════════════════════════════════════════ -->
<script>
// ── STATE ──────────────────────────────────────────────────────────────────
const state = {
  selectedFile: null,
  currentSongs: [],
  wcSongs: [],
  currentTrackIdx: -1,
  sessionHistory: [],
  emotionCounts: {},
  confidences: [],
  songsPlayed: 0,
  emotionChart: null,
  timelineChart: null,
};
const audio = document.getElementById('audio-player');

// FER-2013 approximate class counts for training page
const CLASS_COUNTS = {
  angry:3995, disgust:436, fear:4097, happy:7215,
  neutral:4965, sad:4830, surprise:3171
};
const EMOTION_COLORS = {
  angry:'#ff5c5c', disgust:'#ff9f4a', fear:'#a78bfa',
  happy:'#fbbf24', neutral:'#94a3b8', sad:'#60a5fa', surprise:'#34d399'
};

// ── PAGE NAVIGATION ────────────────────────────────────────────────────────
function showPage(name) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.getElementById('page-' + name).classList.add('active');
  const items = document.querySelectorAll('.nav-item');
  const pages = ['detect','webcam','analysis','training'];
  items[pages.indexOf(name)]?.classList.add('active');
  if (name === 'analysis') renderAnalysis();
  if (name === 'training') renderTraining();
}

// ── FILE UPLOAD ────────────────────────────────────────────────────────────
function onFileSelected(e) {
  state.selectedFile = e.target.files[0];
  if (!state.selectedFile) return;
  const reader = new FileReader();
  reader.onload = ev => {
    const img = document.getElementById('preview-img');
    img.src = ev.target.result;
    img.style.display = 'block';
  };
  reader.readAsDataURL(state.selectedFile);
  document.getElementById('detectBtn').disabled = false;
  document.getElementById('emotion-card').style.display = 'none';
  document.getElementById('songs-card').style.display = 'none';
  document.getElementById('detect-error').innerHTML = '';
}

// Drag & drop
const dz = document.getElementById('drop-zone');
dz.addEventListener('dragover', e => { e.preventDefault(); dz.style.background='#7c4dff22'; });
dz.addEventListener('dragleave', () => { dz.style.background=''; });
dz.addEventListener('drop', e => {
  e.preventDefault(); dz.style.background='';
  const file = e.dataTransfer.files[0];
  if (file) { state.selectedFile = file;
    const inp = document.getElementById('fileInput');
    const dt  = new DataTransfer(); dt.items.add(file); inp.files = dt.files;
    onFileSelected({target:{files:[file]}});
  }
});

// ── DETECT ────────────────────────────────────────────────────────────────
async function runDetection() {
  const btn = document.getElementById('detectBtn');
  btn.disabled = true;
  btn.innerHTML = '<span class="spin"></span> Analyzing…';
  document.getElementById('detect-error').innerHTML = '';

  const fd = new FormData();
  fd.append('image', state.selectedFile);

  try {
    const resp = await fetch('/predict', { method:'POST', body:fd });
    const text = await resp.text();
    let data;
    try { data = JSON.parse(text); }
    catch(e) { throw new Error('Server error — check your terminal.'); }
    if (!resp.ok || data.error) throw new Error(data.error || 'Unknown error');

    showEmotionResult(data);
    showSongs(data.songs, data.emotion, data.emoji);
    recordHistory(data);

    // Auto-play first song with preview
    const first = data.songs.find(s => s.preview_url);
    if (first) playSong(first, data.songs.indexOf(first));

  } catch(err) {
    document.getElementById('detect-error').innerHTML =
      '<div class="error-box">⚠️ ' + err.message + '</div>';
  }
  btn.disabled = false;
  btn.innerHTML = '🔍 Detect Emotion &amp; Play Music';
}

// ── SHOW EMOTION RESULT ───────────────────────────────────────────────────
function showEmotionResult(data) {
  document.getElementById('emotion-card').style.display = 'block';
  document.getElementById('res-emoji').textContent  = data.emoji || '';
  document.getElementById('res-name').textContent   = data.emotion;
  document.getElementById('res-conf').textContent   = 'Confidence: ' + (data.confidence*100).toFixed(1) + '%';
  document.getElementById('res-mood').textContent   = '🎧 ' + (data.mood || '');

  // Confidence bars
  const barsEl = document.getElementById('conf-bars');
  barsEl.innerHTML = '';
  const sorted = Object.entries(data.all_scores).sort((a,b) => b[1]-a[1]);
  sorted.forEach(([label, score]) => {
    const pct = (score*100).toFixed(1);
    barsEl.innerHTML +=
      '<div class="conf-bar-row">' +
      '<span class="conf-label">' + label + '</span>' +
      '<div class="conf-track"><div class="conf-fill" style="width:' + pct + '%"></div></div>' +
      '<span class="conf-pct">' + pct + '%</span>' +
      '</div>';
  });

  // Chart.js bar chart
  if (state.emotionChart) state.emotionChart.destroy();
  const ctx = document.getElementById('emotionChart').getContext('2d');
  const labels = sorted.map(([l]) => l);
  const values = sorted.map(([,v]) => +(v*100).toFixed(1));
  state.emotionChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets:[{
        label:'Confidence %',
        data: values,
        backgroundColor: labels.map(l => (EMOTION_COLORS[l]||'#7c4dff')+'88'),
        borderColor:     labels.map(l => EMOTION_COLORS[l]||'#7c4dff'),
        borderWidth: 1.5, borderRadius: 6,
      }]
    },
    options:{
      responsive:true, maintainAspectRatio:false,
      plugins:{ legend:{display:false} },
      scales:{
        x:{ grid:{color:'#ffffff10'}, ticks:{color:'#6b6b8a',font:{size:11}} },
        y:{ grid:{color:'#ffffff10'}, ticks:{color:'#6b6b8a',font:{size:11}}, max:100,
            title:{display:true,text:'%',color:'#6b6b8a'} }
      }
    }
  });
}

// ── SHOW SONGS ────────────────────────────────────────────────────────────
function showSongs(songs, emotion, emoji, listId='song-list', cardId='songs-card', badgeId='songs-emotion-badge') {
  state.currentSongs = songs;
  document.getElementById(cardId).style.display = 'block';
  if (badgeId) document.getElementById(badgeId).textContent = (emoji||'') + ' ' + emotion;

  const el = document.getElementById(listId);
  el.innerHTML = '';
  songs.forEach((s, i) => {
    const hasPreview = !!s.preview_url;
    el.innerHTML +=
      '<div class="song-card" id="song-row-' + listId + '-' + i + '">' +
      '<span class="song-num">' + (i+1) + '</span>' +
      '<div class="song-info">' +
        '<div class="song-name">' + esc(s.name) + '</div>' +
        '<div class="song-meta">' + esc(s.artist) + (s.year&&s.year!=="N/A"?' · '+s.year:'') + '</div>' +
        '<div class="song-tags">' +
          '<span class="tag tag-genre">' + esc(s.genre) + '</span>' +
          '<span class="tag tag-val">❤ ' + s.valence + '</span>' +
          '<span class="tag tag-energy">⚡ ' + s.energy + '</span>' +
        '</div>' +
      '</div>' +
      '<div class="song-actions">' +
        (hasPreview
          ? '<button class="btn btn-sm btn-play" onclick=\'playSong(' + JSON.stringify(s).replace(/'/g,"&#39;") + ',' + i + ')\'>▶ Play</button>'
          : '<span style="font-size:.72rem;color:var(--muted)">No preview</span>') +
        (s.spotify_id
          ? '<a href="https://open.spotify.com/track/' + s.spotify_id + '" target="_blank" ' +
            'style="font-size:.72rem;color:#1DB954;text-decoration:none;padding:.3rem .5rem;' +
            'background:#1DB95418;border-radius:6px;border:1px solid #1DB95433">Spotify</a>' : '') +
      '</div>' +
      '</div>';
  });
}

// ── AUDIO PLAYER ──────────────────────────────────────────────────────────
let playQueue = [];
let playQueueIdx = -1;

function playSong(song, idx) {
  if (!song.preview_url) { alert('No preview available for this song.'); return; }
  playQueue    = state.currentSongs.filter(s => s.preview_url);
  playQueueIdx = playQueue.findIndex(s => s.name === song.name);
  if (playQueueIdx < 0) { playQueue.unshift(song); playQueueIdx = 0; }
  loadAndPlay(playQueue[playQueueIdx]);
  state.songsPlayed++;
}

function loadAndPlay(song) {
  audio.src = song.preview_url;
  audio.play().catch(()=>{});
  document.getElementById('np-title').textContent  = song.name;
  document.getElementById('np-artist').textContent = song.artist + ' · ' + song.genre;
  document.getElementById('now-playing').style.display = 'flex';
  document.getElementById('np-play').textContent = '⏸';
  document.getElementById('main-content').style.paddingBottom = '70px';
}

function togglePlay() {
  if (audio.paused) { audio.play(); document.getElementById('np-play').textContent='⏸'; }
  else              { audio.pause(); document.getElementById('np-play').textContent='▶'; }
}
function nextTrack() {
  if (playQueue.length===0) return;
  playQueueIdx = (playQueueIdx+1) % playQueue.length;
  loadAndPlay(playQueue[playQueueIdx]);
}
function prevTrack() {
  if (playQueue.length===0) return;
  playQueueIdx = (playQueueIdx-1+playQueue.length) % playQueue.length;
  loadAndPlay(playQueue[playQueueIdx]);
}
function stopPlayer() {
  audio.pause(); audio.src='';
  document.getElementById('now-playing').style.display='none';
  document.getElementById('main-content').style.paddingBottom='2rem';
}

// Update progress bar
audio.addEventListener('timeupdate', () => {
  if (!audio.duration) return;
  const pct = (audio.currentTime / audio.duration)*100;
  document.getElementById('np-bar').value = pct;
  document.getElementById('np-time').textContent = fmt(audio.currentTime)+' / '+fmt(audio.duration);
});
audio.addEventListener('ended', nextTrack);
document.getElementById('np-bar').addEventListener('click', e => {
  const rect = e.target.getBoundingClientRect();
  const pct  = (e.clientX - rect.left) / rect.width;
  audio.currentTime = pct * audio.duration;
});

function fmt(s) {
  const m = Math.floor(s/60), sec = Math.floor(s%60);
  return m+':'+(sec<10?'0':'')+sec;
}

// ── WEBCAM ────────────────────────────────────────────────────────────────
let webcamActive=false, webcamInterval=null, webcamStream=null;

async function toggleWebcam() {
  if (webcamActive) { stopWebcam(); return; }
  try {
    webcamStream = await navigator.mediaDevices.getUserMedia({video:true});
    const video  = document.getElementById('webcam-video');
    video.srcObject = webcamStream;
    await video.play();
    document.getElementById('webcamBtn').textContent = '⏹ Stop Webcam';
    document.getElementById('webcam-status').textContent = 'Scanning every 3 seconds…';
    webcamActive = true;
    captureFrame();
    webcamInterval = setInterval(captureFrame, 3000);
  } catch(e) {
    document.getElementById('webcam-status').textContent = '❌ ' + e.message;
  }
}

function stopWebcam() {
  webcamActive=false; clearInterval(webcamInterval);
  if (webcamStream) webcamStream.getTracks().forEach(t=>t.stop());
  webcamStream=null;
  document.getElementById('webcamBtn').textContent='▶ Start Webcam';
  document.getElementById('webcam-status').textContent='Webcam stopped.';
  const c=document.getElementById('webcam-canvas');
  c.getContext('2d').clearRect(0,0,c.width,c.height);
}

async function captureFrame() {
  const video  = document.getElementById('webcam-video');
  const canvas = document.getElementById('webcam-canvas');
  const ctx    = canvas.getContext('2d');
  ctx.save(); ctx.scale(-1,1);
  ctx.drawImage(video,-canvas.width,0,canvas.width,canvas.height);
  ctx.restore();
  const b64 = canvas.toDataURL('image/jpeg',.85).split(',')[1];
  try {
    const resp = await fetch('/webcam/frame',{method:'POST',
      headers:{'Content-Type':'application/json'},body:JSON.stringify({frame:b64})});
    const text = await resp.text();
    let data; try{data=JSON.parse(text);}catch(e){return;}
    if (data.error) { document.getElementById('webcam-status').textContent='⚠️ '+data.error; return; }
    if (data.annotated_frame) {
      const img=new Image();
      img.onload=()=>ctx.drawImage(img,0,0,canvas.width,canvas.height);
      img.src=data.annotated_frame;
    }
    document.getElementById('webcam-status').textContent =
      (data.face_detected?'✅ Face detected':'🖼 Full frame') +
      ' — ' + data.emotion + ' (' + (data.confidence*100).toFixed(1) + '%)';
    document.getElementById('webcam-emotion-card').style.display='block';
    document.getElementById('wc-emoji').textContent = data.emoji||'';
    document.getElementById('wc-name').textContent  = data.emotion;
    document.getElementById('wc-conf').textContent  = 'Confidence: '+(data.confidence*100).toFixed(1)+'%';
    document.getElementById('wc-mood').textContent  = '🎧 '+(data.mood||'');
    showSongs(data.songs, data.emotion, data.emoji, 'wc-song-list', 'wc-songs-card', null);
    state.wcSongs = data.songs;
    recordHistory(data);
    const first = data.songs.find(s=>s.preview_url);
    if (first && audio.paused) playSong(first, 0);
  } catch(e){console.error(e);}
}

// ── SESSION HISTORY ───────────────────────────────────────────────────────
function recordHistory(data) {
  const entry = {
    time: new Date().toLocaleTimeString(),
    emotion: data.emotion,
    confidence: data.confidence,
    emoji: data.emoji
  };
  state.sessionHistory.unshift(entry);
  state.emotionCounts[data.emotion] = (state.emotionCounts[data.emotion]||0)+1;
  state.confidences.push(+(data.confidence*100).toFixed(1));
}

// ── ANALYSIS PAGE ─────────────────────────────────────────────────────────
function renderAnalysis() {
  const total = state.sessionHistory.length;
  document.getElementById('stat-total').textContent = total;
  document.getElementById('stat-played').textContent = state.songsPlayed;

  if (total === 0) {
    document.getElementById('stat-top').textContent = '—';
    document.getElementById('stat-conf').textContent = '—';
    document.getElementById('emotion-freq').innerHTML =
      '<p style="color:var(--muted);font-size:.85rem">No detections yet. Run a detection first.</p>';
    return;
  }

  // Top emotion
  const top = Object.entries(state.emotionCounts).sort((a,b)=>b[1]-a[1])[0];
  document.getElementById('stat-top').textContent = top[0];
  const avgConf = (state.confidences.reduce((a,b)=>a+b,0)/state.confidences.length).toFixed(1);
  document.getElementById('stat-conf').textContent = avgConf + '%';

  // Frequency bars
  const freqEl = document.getElementById('emotion-freq');
  freqEl.innerHTML = '';
  const maxCount = Math.max(...Object.values(state.emotionCounts));
  Object.entries(state.emotionCounts).sort((a,b)=>b[1]-a[1]).forEach(([emo,cnt]) => {
    const pct = (cnt/maxCount*100).toFixed(0);
    freqEl.innerHTML +=
      '<div class="emo-freq-bar">' +
      '<span class="emo-freq-label">' + emo + '</span>' +
      '<div class="emo-freq-track">' +
        '<div class="emo-freq-fill" style="width:'+pct+'%;background:'+(EMOTION_COLORS[emo]||'var(--accent)')+'"></div>' +
      '</div>' +
      '<span class="emo-freq-count">'+cnt+'</span>' +
      '</div>';
  });

  // Timeline chart
  if (state.timelineChart) state.timelineChart.destroy();
  const ctx2 = document.getElementById('timelineChart').getContext('2d');
  state.timelineChart = new Chart(ctx2, {
    type:'line',
    data:{
      labels: state.sessionHistory.map((_,i)=>'#'+(state.sessionHistory.length-i)).reverse(),
      datasets:[{
        label:'Confidence %',
        data:[...state.confidences],
        borderColor:'#7c4dff',
        backgroundColor:'#7c4dff22',
        fill:true, tension:0.4,
        pointBackgroundColor:'#e040fb', pointRadius:4,
      }]
    },
    options:{
      responsive:true, maintainAspectRatio:false,
      plugins:{legend:{display:false}},
      scales:{
        x:{grid:{color:'#ffffff10'},ticks:{color:'#6b6b8a',font:{size:10}}},
        y:{grid:{color:'#ffffff10'},ticks:{color:'#6b6b8a',font:{size:10}},min:0,max:100,
          title:{display:true,text:'%',color:'#6b6b8a'}}
      }
    }
  });

  // History list
  const histEl = document.getElementById('history-list');
  histEl.innerHTML = '';
  state.sessionHistory.forEach(h => {
    histEl.innerHTML +=
      '<div style="display:flex;align-items:center;gap:.75rem;padding:.6rem 0;' +
      'border-bottom:1px solid var(--border)">' +
      '<span style="font-size:1.2rem">'+(h.emoji||'🎭')+'</span>' +
      '<span style="font-size:.88rem;text-transform:capitalize;flex:1">'+h.emotion+'</span>' +
      '<span style="font-size:.8rem;color:var(--muted)">'+(h.confidence*100).toFixed(1)+'%</span>' +
      '<span style="font-size:.76rem;color:var(--muted)">'+h.time+'</span>' +
      '</div>';
  });
}

// ── TRAINING PAGE ─────────────────────────────────────────────────────────
function noModelMsg() {
  return '<div class="no-model-msg">' +
    '<p style="font-size:1.5rem;margin-bottom:.5rem">🧠</p>' +
    '<p>Training curves not found.</p>' +
    '<p style="margin-top:.4rem;font-size:.8rem">Run: <code>python src/train_model_v2.py</code></p>' +
    '</div>';
}

function renderTraining() {
  // Class distribution chart
  const ctx3 = document.getElementById('classDistChart').getContext('2d');
  const labels = Object.keys(CLASS_COUNTS);
  const values = Object.values(CLASS_COUNTS);
  new Chart(ctx3, {
    type:'doughnut',
    data:{
      labels,
      datasets:[{
        data:values,
        backgroundColor:labels.map(l=>(EMOTION_COLORS[l]||'#7c4dff')+'cc'),
        borderColor:'#0d0d14', borderWidth:2,
      }]
    },
    options:{
      responsive:true, maintainAspectRatio:false,
      plugins:{legend:{position:'right',labels:{color:'#6b6b8a',font:{size:11},padding:10}}}
    }
  });

  // Class detail table
  const detailEl = document.getElementById('class-detail');
  const total = Object.values(CLASS_COUNTS).reduce((a,b)=>a+b,0);
  detailEl.innerHTML =
    '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:.75rem">' +
    labels.map(emo => {
      const cnt = CLASS_COUNTS[emo];
      const pct = (cnt/total*100).toFixed(1);
      return '<div style="background:#ffffff06;border:1px solid var(--border);border-radius:8px;padding:.75rem">' +
        '<div style="display:flex;align-items:center;gap:.4rem;margin-bottom:.4rem">' +
          '<span style="width:10px;height:10px;border-radius:50%;background:'+(EMOTION_COLORS[emo]||'#7c4dff')+';display:inline-block"></span>' +
          '<span style="font-size:.85rem;text-transform:capitalize;font-weight:500">' + emo + '</span>' +
        '</div>' +
        '<div style="font-size:1.1rem;font-weight:700">' + cnt.toLocaleString() + '</div>' +
        '<div style="font-size:.75rem;color:var(--muted)">' + pct + '% of dataset</div>' +
        '</div>';
    }).join('') +
    '</div>';
}

// ── HELPERS ───────────────────────────────────────────────────────────────
function esc(s) {
  return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

// Init training page stats on load
window.addEventListener('load', () => {
  document.getElementById('main-content').style.paddingBottom = '2rem';
});
</script>
</body>
</html>
"""


# ──────────────────────────────────────────────────────────────────────────────
# ROUTES
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template_string(INDEX_HTML)

@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "No image file"}), 400
    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    ext      = os.path.splitext(file.filename)[1].lower() or ".jpg"
    tmp_path = os.path.join(UPLOAD_FOLDER, f"up_{uuid.uuid4().hex}{ext}")
    file.save(tmp_path)

    try:
        result = _process_image_file(tmp_path)
        return jsonify(result)
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        logger.exception("Prediction error")
        return jsonify({"error": str(e)}), 500
    finally:
        gc.collect()
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except PermissionError:
            pass


@app.route("/webcam/frame", methods=["POST"])
def webcam_frame():
    data = request.get_json(silent=True)
    if not data or "frame" not in data:
        return jsonify({"error": "No frame data"}), 400
    try:
        import cv2
        img_bytes = base64.b64decode(data["frame"])
        nparr     = np.frombuffer(img_bytes, np.uint8)
        frame     = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if frame is None:
            return jsonify({"error": "Could not decode frame"}), 400

        faces = detect_faces(frame)
        if faces:
            largest   = max(faces, key=lambda b: b[2]*b[3])
            face_crop = crop_face(frame, largest)
            pred      = predict_from_array(face_crop)
            emo       = pred["emotion"]
            label     = f"{emotion_emoji(emo)} {emo} {pred['confidence']*100:.0f}%"
            annotated = draw_face_box(frame, largest, label=label)
            ann_b64   = image_to_base64(annotated)
        else:
            pred    = predict_from_array(frame)
            emo     = pred["emotion"]
            ann_b64 = image_to_base64(frame)

        info  = get_emotion_info(emo)
        songs = recommender.recommend(emo, n=8)
        return jsonify({
            "emotion": emo, "confidence": pred["confidence"],
            "all_scores": pred["all_scores"], "mood": info["mood"],
            "emoji": emotion_emoji(emo), "songs": songs,
            "annotated_frame": ann_b64, "face_detected": bool(faces),
        })
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        logger.exception("Webcam error")
        return jsonify({"error": str(e)}), 500


def _process_image_file(image_path):
    import cv2
    frame = cv2.imread(image_path)
    if frame is None:
        from PIL import Image as PILImage
        pil_img = PILImage.open(image_path).convert("RGB")
        frame   = np.array(pil_img)[:, :, ::-1]

    faces = detect_faces(frame)
    if faces:
        largest   = max(faces, key=lambda b: b[2]*b[3])
        face_crop = crop_face(frame, largest)
        pred      = predict_from_array(face_crop)
    else:
        pred = predict_from_path(image_path)

    emo   = pred["emotion"]
    info  = get_emotion_info(emo)
    songs = recommender.recommend(emo, n=10)
    return {
        "emotion": emo, "confidence": pred["confidence"],
        "all_scores": pred["all_scores"], "mood": info["mood"],
        "emoji": emotion_emoji(emo), "songs": songs,
        "face_detected": bool(faces),
    }


if __name__ == "__main__":
    print("\n" + "="*50)
    print("  MoodMate v3 — Dashboard")
    print("  Open: http://localhost:5000")
    print("="*50 + "\n")
    app.run(host="0.0.0.0", port=5000, debug=True)
