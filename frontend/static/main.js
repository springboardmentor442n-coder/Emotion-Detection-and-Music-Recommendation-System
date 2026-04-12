// ── DOM References ──────────────────────────────────────────
const btnCamera     = document.getElementById('btn-camera');
const btnUpload     = document.getElementById('btn-upload');
const cameraInput   = document.getElementById('camera-input');
const uploadInput   = document.getElementById('upload-input');
const btnSubmitText = document.getElementById('btn-submit-text');
const feelingInput  = document.getElementById('feeling-input');
const resultSection = document.getElementById('result-section');
const moodResult    = document.getElementById('mood-result');
const emotionEmoji  = document.getElementById('emotion-emoji');
const songGrid      = document.getElementById('song-grid');
const loadingSpinner = document.getElementById('loading');
const tabBtns       = document.querySelectorAll('.tab-btn');
const tabPanes      = document.querySelectorAll('.tab-pane');

// ── Emotion Data ────────────────────────────────────────────
const emotionEmojis = {
  angry:    '😠',
  fear:     '😨',
  happy:    '😊',
  neutral:  '😐',
  sad:      '😢',
  surprise: '😲'
};

const emotionColors = {
  angry:    '#f87171',
  fear:     '#a78bfa',
  happy:    '#fbbf24',
  neutral:  '#60a5fa',
  sad:      '#818cf8',
  surprise: '#34d399'
};

// ── Tab Switching ───────────────────────────────────────────
tabBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    const tabName = btn.getAttribute('data-tab');
    
    tabBtns.forEach(b => b.classList.remove('active'));
    tabPanes.forEach(p => p.classList.remove('active'));
    
    btn.classList.add('active');
    document.getElementById(tabName).classList.add('active');
  });
});

// ── Camera Button ────────────────────────────────────────────
btnCamera.addEventListener('click', async () => {
  const isMobile = /Android|iPhone|iPad|iPod/i.test(navigator.userAgent);

  if (isMobile) {
    cameraInput.setAttribute('capture', 'user');
    cameraInput.click();
  } else {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });

      const overlay = document.createElement('div');
      overlay.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.9);z-index:9999;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:20px;';

      const video = document.createElement('video');
      video.autoplay = true;
      video.playsInline = true;
      video.srcObject = stream;
      video.style.cssText = 'width:500px;max-width:90vw;height:auto;border-radius:12px;transform:scaleX(-1);box-shadow:0 20px 60px rgba(0,0,0,0.3);';

      const snapBtn = document.createElement('button');
      snapBtn.innerHTML = '<i class="fas fa-camera"></i> Take Photo';
      snapBtn.style.cssText = 'padding:14px 36px;background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);color:white;border:none;border-radius:50px;font-size:1rem;font-weight:700;cursor:pointer;font-family:Poppins;box-shadow:0 8px 25px rgba(102, 126, 234, 0.4);';

      const cancelBtn = document.createElement('button');
      cancelBtn.innerHTML = '<i class="fas fa-times"></i> Cancel';
      cancelBtn.style.cssText = 'padding:12px 32px;background:transparent;color:white;border:2px solid rgba(255,255,255,0.5);border-radius:50px;font-size:0.95rem;font-weight:600;cursor:pointer;font-family:Poppins;';

      overlay.appendChild(video);
      overlay.appendChild(snapBtn);
      overlay.appendChild(cancelBtn);
      document.body.appendChild(overlay);

      const closeModal = () => {
        stream.getTracks().forEach(t => t.stop());
        document.body.removeChild(overlay);
      };

      snapBtn.addEventListener('click', () => {
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext('2d').drawImage(video, 0, 0);
        const base64Image = canvas.toDataURL('image/jpeg', 0.9);
        closeModal();
        sendImageToBackend(base64Image);
      });

      cancelBtn.addEventListener('click', closeModal);

    } catch (err) {
      if (err.name === 'NotAllowedError') {
        alert('❌ Camera permission denied. Please allow camera access in your browser settings.');
      } else if (err.name === 'NotFoundError') {
        alert('❌ No camera found on this device.');
      } else {
        alert('❌ Could not access camera: ' + err.message);
      }
    }
  }
});

cameraInput.addEventListener('change', (e) => {
  const file = e.target.files[0];
  if (file) handleImageFile(file);
  cameraInput.value = '';
});

// ── Upload Button ────────────────────────────────────────────
btnUpload.addEventListener('click', () => uploadInput.click());
uploadInput.addEventListener('change', (e) => {
  const file = e.target.files[0];
  if (file) handleImageFile(file);
  uploadInput.value = '';
});

// ── Convert Image to Base64 ──────────────────────────────────
function handleImageFile(file) {
  const reader = new FileReader();
  reader.onload = (e) => {
    sendImageToBackend(e.target.result);
  };
  reader.readAsDataURL(file);
}

// ── Text Submit ──────────────────────────────────────────────
btnSubmitText.addEventListener('click', () => {
  const text = feelingInput.value.trim();
  if (!text) {
    alert('Please tell us how you are feeling!');
    return;
  }
  sendTextToBackend(text);
});

feelingInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') btnSubmitText.click();
});

// ── Send Image to Backend ────────────────────────────────────
async function sendImageToBackend(base64Image) {
  showLoading();
  try {
    const response = await fetch('/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image: base64Image })
    });

    const data = await response.json();

    if (data.error) {
      alert('❌ Error: ' + data.error);
      return;
    }

    displayResults(data.emotion, data.confidence, data.all_scores, data.songs);

  } catch (err) {
    alert('❌ Could not connect to server. Make sure the backend is running on http://127.0.0.1:5000');
    console.error(err);
  } finally {
    hideLoading();
  }
}

// ── Send Text to Backend ─────────────────────────────────────
async function sendTextToBackend(text) {
  showLoading();
  try {
    const response = await fetch('/predict-text', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: text })
    });

    const data = await response.json();

    if (data.error) {
      alert('❌ Error: ' + data.error);
      return;
    }

    const allScores = data.all_scores || {};
    const confidence = data.confidence || 85;
    
    displayResults(data.emotion, confidence, allScores, data.songs);

  } catch (err) {
    alert('❌ Could not connect to server. Make sure the backend is running on http://127.0.0.1:5000');
    console.error(err);
  } finally {
    hideLoading();
  }
}

// ── Display Results ──────────────────────────────────────────
function displayResults(emotion, confidence, allScores, songs) {
  const emoji = emotionEmojis[emotion] || '🎵';
  const color = emotionColors[emotion] || '#667eea';
  const emotionName = emotion.charAt(0).toUpperCase() + emotion.slice(1);

  emotionEmoji.textContent = emoji;
  moodResult.textContent = emotionName;

  const confidenceFill = document.getElementById('confidence-fill');
  const confidenceText = document.getElementById('confidence-text');
  confidenceFill.style.width = confidence + '%';
  confidenceFill.style.background = color;
  confidenceText.textContent = confidence + '%';

  updateEmotionBreakdown(allScores, color);
  displaySongs(songs, color);

  resultSection.classList.remove('hidden');
  setTimeout(() => {
    resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }, 100);
}

// ── Update Emotion Breakdown ─────────────────────────────────
function updateEmotionBreakdown(scores, primaryColor) {
  const emotionBars = document.getElementById('emotion-bars');
  emotionBars.innerHTML = '';

  const emotions = ['angry', 'fear', 'happy', 'neutral', 'sad', 'surprise'];
  
  emotions.forEach(emotion => {
    const score = scores[emotion] || 0;
    const bar = document.createElement('div');
    bar.className = 'emotion-bar';
    
    const emotionLabel = emotion.charAt(0).toUpperCase() + emotion.slice(1);
    const color = emotionColors[emotion] || '#ccc';
    
    bar.innerHTML = `
      <div class="emotion-bar-label">${emotionLabel}</div>
      <div class="emotion-bar-track">
        <div class="emotion-bar-fill" style="width: ${score}%; background: ${color};"></div>
      </div>
      <div class="emotion-bar-value">${score}%</div>
    `;
    
    emotionBars.appendChild(bar);
  });
}

// ── Display Songs ────────────────────────────────────────────
function displaySongs(songs, accentColor) {
  songGrid.innerHTML = '';

  if (!songs || songs.length === 0) {
    songGrid.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: #999;">No songs found for this mood.</p>';
    return;
  }

  let currentAudio = null;
  let currentBtn = null;
  let currentIcon = null;

  songs.forEach((song, i) => {
    const card = document.createElement('div');
    card.className = 'song-card';

    const rawUrl = (song.preview_url || '').trim();
    const safeUrl = rawUrl.replace('http://', 'https://');
    const hasPreview = safeUrl && safeUrl !== 'nan' && safeUrl !== 'None' && safeUrl !== 'NaN';

    const songTitle = escapeHtml(song.song || 'Unknown Song');
    const artistName = escapeHtml(song.artist || 'Unknown Artist');

    card.innerHTML = `
      <div class="album-art">🎵</div>
      <div class="song-info">
        <h3>${songTitle}</h3>
        <p>${artistName}</p>
      </div>
      <button class="play-btn" id="play-btn-${i}" ${!hasPreview ? 'disabled' : ''} title="${hasPreview ? 'Play 30s preview' : 'No preview available'}">
        <i class="fas fa-play" id="play-icon-${i}"></i>
      </button>
    `;

    if (hasPreview) {
      const btn = card.querySelector(`#play-btn-${i}`);
      const icon = card.querySelector(`#play-icon-${i}`);

      btn.addEventListener('click', () => {
        if (currentAudio && currentBtn === btn) {
          currentAudio.pause();
          currentAudio = null;
          icon.className = 'fas fa-play';
          btn.style.background = '';
          btn.style.color = '';
          currentBtn = null;
          currentIcon = null;
          return;
        }

        if (currentAudio) {
          currentAudio.pause();
          currentAudio = null;
          currentIcon.className = 'fas fa-play';
          currentBtn.style.background = '';
          currentBtn.style.color = '';
        }

        currentAudio = new Audio(safeUrl);
        currentAudio.volume = 0.8;
        currentBtn = btn;
        currentIcon = icon;

        currentAudio.play()
          .then(() => {
            icon.className = 'fas fa-pause';
            btn.style.background = accentColor;
            btn.style.color = 'white';
          })
          .catch((err) => {
            console.error('Playback failed:', err);
            currentAudio = null;
            currentBtn = null;
            currentIcon = null;
            alert('Could not play preview. The audio link may have expired.');
          });

        currentAudio.addEventListener('ended', () => {
          icon.className = 'fas fa-play';
          btn.style.background = '';
          btn.style.color = '';
          currentAudio = null;
          currentBtn = null;
          currentIcon = null;
        });
      });
    }

    songGrid.appendChild(card);
  });
}

// ── Loading State ────────────────────────────────────────────
function showLoading() {
  loadingSpinner.classList.remove('hidden');
  btnCamera.disabled = true;
  btnUpload.disabled = true;
  btnSubmitText.disabled = true;
}

function hideLoading() {
  loadingSpinner.classList.add('hidden');
  btnCamera.disabled = false;
  btnUpload.disabled = false;
  btnSubmitText.disabled = false;
}

// ── Reset UI ─────────────────────────────────────────────────
function resetUI() {
  resultSection.classList.add('hidden');
  feelingInput.value = '';
  songGrid.innerHTML = '';
  tabBtns[0].click();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ── Utility: Escape HTML ─────────────────────────────────────
function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
