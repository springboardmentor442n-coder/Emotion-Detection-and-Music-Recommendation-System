// ── DOM refs ────────────────────────────────────────────────
const btnCamera     = document.getElementById('btn-camera');
const btnUpload     = document.getElementById('btn-upload');
const cameraInput   = document.getElementById('camera-input');
const uploadInput   = document.getElementById('upload-input');
const btnSubmitText = document.getElementById('btn-submit-text');
const feelingInput  = document.getElementById('feeling-input');
const resultSection = document.getElementById('result-section');
const moodResult    = document.getElementById('mood-result');
const songGrid      = document.getElementById('song-grid');

// ── Emotion colors & emojis ──────────────────────────────────
const emotionColors = {
  angry:    '#f87171',
  fear:     '#a78bfa',
  happy:    '#fbbf24',
  neutral:  '#60a5fa',
  sad:      '#818cf8',
  surprise: '#34d399'
};

const emotionEmoji = {
  angry:    '😠',
  fear:     '😨',
  happy:    '😊',
  neutral:  '😐',
  sad:      '😢',
  surprise: '😲'
};

// ── Camera button ────────────────────────────────────────────
btnCamera.addEventListener('click', async () => {
  const isMobile = /Android|iPhone|iPad|iPod/i.test(navigator.userAgent);

  if (isMobile) {
    // On mobile: open native camera directly
    cameraInput.setAttribute('capture', 'user');
    cameraInput.click();
  } else {
    // On desktop: use getUserMedia for live webcam
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });

      // Build a simple modal on the fly
      const overlay = document.createElement('div');
      overlay.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.8);z-index:9999;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:16px;';

      const video = document.createElement('video');
      video.autoplay = true;
      video.playsInline = true;
      video.srcObject = stream;
      video.style.cssText = 'width:480px;max-width:90vw;border-radius:12px;transform:scaleX(-1);';

      const snapBtn = document.createElement('button');
      snapBtn.textContent = '📸 Take Photo';
      snapBtn.style.cssText = 'padding:12px 32px;background:#8b5cf6;color:white;border:none;border-radius:8px;font-size:1rem;font-weight:700;cursor:pointer;';

      const cancelBtn = document.createElement('button');
      cancelBtn.textContent = 'Cancel';
      cancelBtn.style.cssText = 'padding:8px 24px;background:transparent;color:white;border:1px solid rgba(255,255,255,0.4);border-radius:8px;font-size:0.9rem;cursor:pointer;';

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
        canvas.width  = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext('2d').drawImage(video, 0, 0);
        const base64Image = canvas.toDataURL('image/jpeg', 0.9);
        closeModal();
        sendImageToBackend(base64Image);
      });

      cancelBtn.addEventListener('click', closeModal);

    } catch (err) {
      if (err.name === 'NotAllowedError') {
        alert('Camera permission denied. Please allow camera access in your browser settings.');
      } else if (err.name === 'NotFoundError') {
        alert('No camera found on this device.');
      } else {
        alert('Could not access camera: ' + err.message);
      }
    }
  }
});

cameraInput.addEventListener('change', (e) => {
  const file = e.target.files[0];
  if (file) handleImageFile(file);
  cameraInput.value = '';
});

// ── Upload button ────────────────────────────────────────────
btnUpload.addEventListener('click', () => uploadInput.click());
uploadInput.addEventListener('change', (e) => {
  const file = e.target.files[0];
  if (file) handleImageFile(file);
});

// ── Convert image to base64 and send ────────────────────────
function handleImageFile(file) {
  const reader = new FileReader();
  reader.onload = (e) => {
    sendImageToBackend(e.target.result);
  };
  reader.readAsDataURL(file);
}

// ── Text submit ──────────────────────────────────────────────
btnSubmitText.addEventListener('click', () => {
  const text = feelingInput.value.trim();
  if (!text) {
    alert('Please enter how you are feeling.');
    return;
  }
  sendTextToBackend(text);
});

feelingInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') btnSubmitText.click();
});

// ── Send image to backend ────────────────────────────────────
async function sendImageToBackend(base64Image) {
  showLoading('Analysing your face...');
  try {
    const response = await fetch('/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image: base64Image })
    });

    const data = await response.json();

    if (data.error) {
      alert('Error: ' + data.error);
      return;
    }

    displayResults(data.emotion, data.songs);

  } catch (err) {
    alert('Could not connect to server. Make sure the backend is running on port 5000.');
    console.error(err);
  } finally {
    hideLoading();
  }
}

// ── Send text to backend ─────────────────────────────────────
async function sendTextToBackend(text) {
  showLoading('Analysing your mood...');
  try {
    const response = await fetch('/predict-text', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: text })
    });

    const data = await response.json();

    if (data.error) {
      alert('Error: ' + data.error);
      return;
    }

    displayResults(data.emotion, data.songs);

  } catch (err) {
    alert('Could not connect to server. Make sure the backend is running on port 5000.');
    console.error(err);
  } finally {
    hideLoading();
  }
}

// ── Display results ──────────────────────────────────────────
function displayResults(emotion, songs) {
  const color = emotionColors[emotion] || '#7c6aff';
  const emoji = emotionEmoji[emotion] || '🎵';

  // Update mood label
  moodResult.textContent = emoji + ' ' + emotion.charAt(0).toUpperCase() + emotion.slice(1);
  moodResult.style.color = color;

  // Clear old songs
  songGrid.innerHTML = '';

  if (!songs || songs.length === 0) {
    songGrid.innerHTML = '<p>No songs found for this mood.</p>';
  } else {

    // ✅ Shared across ALL song cards — tracks what is currently playing
    let currentAudio = null;
    let currentBtn   = null;
    let currentIcon  = null;

    songs.forEach((song, i) => {
      const card = document.createElement('div');
      card.className = 'song-card';
      card.style.animationDelay = `${i * 0.07}s`;

      // ✅ FIX: trim whitespace and force https
      const rawUrl    = (song.preview_url || '').trim();
      const safeUrl   = rawUrl.replace('http://', 'https://');
      const hasPreview = safeUrl !== '' && safeUrl !== 'nan' && safeUrl !== 'None' && safeUrl !== 'NaN';

      card.innerHTML = `
        <div class="song-number" style="color:${color}">0${i + 1}</div>
        <div class="song-details">
          <div class="song-title">${escapeHtml(song.song)}</div>
          <div class="song-artist">${escapeHtml(song.artist)}</div>
        </div>
        <button class="play-btn" id="play-btn-${i}" ${!hasPreview ? 'disabled title="No preview available"' : 'title="Play 30s preview"'}>
          <i class="fas fa-play" id="play-icon-${i}"></i>
        </button>
      `;

      if (hasPreview) {
        const btn  = card.querySelector(`#play-btn-${i}`);
        const icon = card.querySelector(`#play-icon-${i}`);

        btn.addEventListener('click', () => {

          // ✅ If THIS button is already playing, pause and reset it
          if (currentAudio && currentBtn === btn) {
            currentAudio.pause();
            currentAudio          = null;
            icon.className        = 'fas fa-play';
            btn.style.background  = '';
            btn.style.borderColor = '';
            btn.style.color       = '';
            currentBtn  = null;
            currentIcon = null;
            return;
          }

          // ✅ Stop the previously playing song (a different button)
          if (currentAudio) {
            currentAudio.pause();
            currentAudio                 = null;
            currentIcon.className        = 'fas fa-play';
            currentBtn.style.background  = '';
            currentBtn.style.borderColor = '';
            currentBtn.style.color       = '';
          }

          // ✅ FIX: use safeUrl and handle play() Promise properly
          currentAudio        = new Audio(safeUrl);
          currentAudio.volume = 0.8;
          currentBtn          = btn;
          currentIcon         = icon;

          currentAudio.play()
            .then(() => {
              // Playback started successfully
              icon.className        = 'fas fa-pause';
              btn.style.background  = color;
              btn.style.borderColor = color;
              btn.style.color       = '#fff';
            })
            .catch((err) => {
              // Playback failed — reset button state and show error
              console.error('Playback failed:', err);
              currentAudio = null;
              currentBtn   = null;
              currentIcon  = null;
              alert('Could not play preview. The audio link may have expired.');
            });

          // ✅ Reset when the song naturally ends
          currentAudio.addEventListener('ended', () => {
            icon.className        = 'fas fa-play';
            btn.style.background  = '';
            btn.style.borderColor = '';
            btn.style.color       = '';
            currentAudio = null;
            currentBtn   = null;
            currentIcon  = null;
          });
        });
      }

      songGrid.appendChild(card);
    });
  }

  // Show result section with smooth scroll
  resultSection.classList.remove('hidden');
  resultSection.scrollIntoView({ behavior: 'smooth' });
}

// ── Loading state ────────────────────────────────────────────
function showLoading(message = 'Analysing...') {
  btnSubmitText.textContent = message;
  btnSubmitText.disabled = true;
  btnCamera.disabled = true;
  btnUpload.disabled = true;

  // Clear previous results while loading
  moodResult.textContent = '...';
  moodResult.style.color = '#999';
  songGrid.innerHTML = `
    <div class="loading-songs">
      <i class="fas fa-spinner fa-spin"></i>
      <p>Finding your perfect songs...</p>
    </div>
  `;
  resultSection.classList.remove('hidden');
}

function hideLoading() {
  btnSubmitText.textContent = 'Submit';
  btnSubmitText.disabled = false;
  btnCamera.disabled = false;
  btnUpload.disabled = false;
}

// ── Utility ──────────────────────────────────────────────────
function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}