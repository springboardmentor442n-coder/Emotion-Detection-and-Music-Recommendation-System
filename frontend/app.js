document.addEventListener('DOMContentLoaded', () => {
    // API Configuration
    const API_BASE_URL = "http://localhost:8000";

    // --- Tab Logic ---
    const tabs = document.querySelectorAll('.tab-btn');
    const sections = document.querySelectorAll('.input-section');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            sections.forEach(s => s.classList.remove('active'));

            tab.classList.add('active');
            document.getElementById(tab.dataset.target).classList.add('active');

            // Cleanup camera if navigating away
            if (tab.dataset.target !== 'camera-input') {
                stopCamera();
            }
        });
    });

    // --- Core API Helper ---
    async function fetchRecommendation(endpoint, body) {
        showLoading();
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            const data = await response.json();

            if (!response.ok) {
                let errStr = data.detail;
                if (typeof errStr === 'object') errStr = JSON.stringify(errStr);
                throw new Error(errStr || 'An error occurred server-side.');
            }

            showResult(data);
        } catch (error) {
            console.error(error);
            showError("We encountered a problem: " + error.message);
        }
    }

    // --- Text Input Handling ---
    const textEntry = document.getElementById('text-entry');
    const analyzeTextBtn = document.getElementById('analyze-text-btn');

    analyzeTextBtn.addEventListener('click', () => {
        const text = textEntry.value.trim();
        if (text) {
            fetchRecommendation('/api/predict/text', { text });
        } else {
            textEntry.focus();
        }
    });

    // --- Upload Handling ---
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const uploadPreview = document.getElementById('upload-preview');
    const previewContainer = document.getElementById('preview-container');
    const analyzeUploadBtn = document.getElementById('analyze-upload-btn');
    let currentBase64Image = '';

    dropZone.addEventListener('click', () => fileInput.click());

    // Drag and drop cosmetics
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = "var(--primary-light)";
        dropZone.style.background = "rgba(138, 43, 226, 0.1)";
    });
    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = "rgba(177, 107, 255, 0.4)";
        dropZone.style.background = "rgba(0,0,0,0.1)";
    });
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = "rgba(177, 107, 255, 0.4)";
        dropZone.style.background = "rgba(0,0,0,0.1)";
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleImageUpload(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files[0]) {
            handleImageUpload(e.target.files[0]);
        }
    });

    function handleImageUpload(file) {
        if (!file.type.match('image.*')) {
            alert("Please select a valid image file.");
            return;
        }
        const reader = new FileReader();
        reader.onload = (e) => {
            currentBase64Image = e.target.result;
            uploadPreview.src = currentBase64Image;
            dropZone.style.display = 'none';
            previewContainer.style.display = 'block';
        };
        reader.readAsDataURL(file);
    }
    
    const removePhotoBtn = document.getElementById('remove-photo-btn');
    if (removePhotoBtn) {
        removePhotoBtn.addEventListener('click', () => {
            currentBase64Image = '';
            uploadPreview.src = '';
            fileInput.value = '';
            previewContainer.style.display = 'none';
            dropZone.style.display = 'block';
        });
    }

    analyzeUploadBtn.addEventListener('click', () => {
        if (currentBase64Image) {
            fetchRecommendation('/api/predict/image', { image_base64: currentBase64Image });
        }
    });

    // --- Camera Handling ---
    const video = document.getElementById('webcam');
    const canvas = document.getElementById('canvas');
    const startCamBtn = document.getElementById('start-camera');
    const captureBtn = document.getElementById('capture-photo');
    const cameraOverlay = document.getElementById('camera-overlay');
    let stream = null;

    function stopCamera() {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            video.srcObject = null;
            stream = null;
            startCamBtn.textContent = 'Start Camera';
            startCamBtn.style.background = "";
            captureBtn.disabled = true;
            cameraOverlay.style.display = 'none';
        }
    }

    startCamBtn.addEventListener('click', async () => {
        if (stream) {
            stopCamera();
        } else {
            try {
                stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" } });
                video.srcObject = stream;
                startCamBtn.textContent = 'Stop Camera';
                startCamBtn.style.background = "rgba(255, 51, 102, 0.2)";
                captureBtn.disabled = false;
                cameraOverlay.style.display = 'block';
            } catch (err) {
                alert("Cannot access camera. Please check permissions.");
                console.error(err);
            }
        }
    });

    captureBtn.addEventListener('click', () => {
        if (!stream) return;
        // visual feedback
        video.style.opacity = '0.5';
        setTimeout(() => video.style.opacity = '1', 150);

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        // flip context if facing user to act like mirror
        ctx.translate(canvas.width, 0);
        ctx.scale(-1, 1);
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

        const imgData = canvas.toDataURL('image/jpeg', 0.85);
        fetchRecommendation('/api/predict/image', { image_base64: imgData });
    });

    // --- UI State Management ---
    const emptyState = document.getElementById('empty-state');
    const loadingState = document.getElementById('loading-state');
    const contentState = document.getElementById('content-state');
    const errorState = document.getElementById('error-state');
    const errorMsg = document.getElementById('error-message');

    function hideAllStates() {
        [emptyState, loadingState, contentState, errorState].forEach(s => s.classList.remove('active'));
    }

    function showLoading() {
        hideAllStates();
        loadingState.classList.add('active');
    }

    function showError(msg) {
        hideAllStates();
        errorMsg.textContent = msg;
        errorState.classList.add('active');
    }

    function showResult(data) {
        hideAllStates();

        // Update header
        const em = data.emotion;
        document.getElementById('detected-emotion').textContent = em;
        document.getElementById('confidence-score').textContent = `${(data.confidence * 100).toFixed(1)}% Match`;

        // Dynamically color based on emotion (optional enhancement)
        const banner = document.querySelector('.emotion-banner');
        const colorMap = {
            happy: 'linear-gradient(135deg, rgba(255, 204, 0, 0.2), rgba(255, 102, 0, 0.2))',
            sad: 'linear-gradient(135deg, rgba(51, 153, 255, 0.2), rgba(0, 51, 204, 0.2))',
            angry: 'linear-gradient(135deg, rgba(255, 51, 51, 0.2), rgba(153, 0, 0, 0.2))',
            fear: 'linear-gradient(135deg, rgba(102, 0, 153, 0.2), rgba(0, 0, 0, 0.4))',
            surprise: 'linear-gradient(135deg, rgba(51, 204, 204, 0.2), rgba(0, 255, 204, 0.2))',
            disgust: 'linear-gradient(135deg, rgba(153, 204, 51, 0.2), rgba(51, 102, 0, 0.2))',
            neutral: 'linear-gradient(135deg, rgba(138, 43, 226, 0.2), rgba(255, 51, 102, 0.15))' // default
        };
        banner.style.background = colorMap[em.toLowerCase()] || colorMap.neutral;

        // Populate Songs
        const songList = document.getElementById('song-list');
        songList.innerHTML = '';

        if (data.recommendations && data.recommendations.length > 0) {
            data.recommendations.forEach(song => {
                const coverUrl = song.AlbumCover || 'https://via.placeholder.com/65/2a2a2a/ffffff?text=♫';

                const url = song.Link || song.Preview || song.url || song.AudioUrl || '';

                let mediaElement = '';
                if (url) {
                    // Check if it's a direct audio link like Spotify mp3-preview
                    if (url.includes('.mp3') || url.includes('scdn.co') || url.includes('audio') || url.includes('preview')) {
                        mediaElement = `
                            <div style="margin-top: 15px; width: 100%;">
                                <audio controls style="height: 35px; width: 100%; border-radius: 8px;">
                                    <source src="${url}" type="audio/mpeg">
                                    Your browser does not support the audio element.
                                </audio>
                            </div>
                        `;
                    } else {
                        // Otherwise it's probably a YouTube or web link (which can't be put in an <audio> tag)
                        mediaElement = `<a href="${url}" target="_blank" style="color: var(--primary-light); text-decoration: none; font-size: 0.95rem; margin-top: 8px; display: inline-block; font-weight: 600;">Listen on Web →</a>`;
                    }
                }

                const html = `
                    <div class="song-item" style="flex-direction: column; align-items: stretch;">
                        <div style="display: flex; align-items: center; width: 100%;">
                            <img src="${coverUrl}" class="song-cover" alt="Album Cover">
                            <div class="song-info">
                                <div class="song-title">${song.Song}</div>
                                <div class="song-artist">${song.Artist} • ${song.Genre}</div>
                                ${!mediaElement.includes('<audio') ? mediaElement : ''}
                            </div>
                        </div>
                        ${mediaElement.includes('<audio') ? mediaElement : ''}
                    </div>
                `;
                songList.innerHTML += html;
            });
        } else {
            songList.innerHTML = `<p style="color: var(--text-muted); text-align: center;">No music found for this mood.</p>`;
        }

        contentState.classList.add('active');
    }
});
