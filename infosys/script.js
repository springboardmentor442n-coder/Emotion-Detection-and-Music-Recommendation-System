let mode = "text"; // default

const inputArea = document.getElementById("inputArea");
const textBtn = document.getElementById("textBtn");
const uploadBtn = document.getElementById("uploadBtn");

/* Render Text Input */
function showTextInput() {
    mode = "text";

    inputArea.innerHTML = `
        <textarea id="textInput" placeholder="Enter your text..."></textarea>
    `;

    textBtn.classList.add("active");
    uploadBtn.classList.remove("active");
}

/* Render Upload Input */
function showUploadInput() {
    mode = "upload";

    inputArea.innerHTML = `
        <input type="file" id="imageInput" accept="image/*">
        <img id="preview" class="preview">
    `;

    const imageInput = document.getElementById("imageInput");
    const preview = document.getElementById("preview");

    imageInput.addEventListener("change", function () {
        const file = this.files[0];
        if (file) {
            preview.src = URL.createObjectURL(file);
            preview.style.display = "block";
        }
    });

    uploadBtn.classList.add("active");
    textBtn.classList.remove("active");
}

/* Button Events */
textBtn.addEventListener("click", showTextInput);
uploadBtn.addEventListener("click", showUploadInput);

/* Default load */
showTextInput();

/* Prediction */
async function predictEmotion() {
    let formData = new FormData();

    if (mode === "text") {
        const text = document.getElementById("textInput").value;
        formData.append("text", text);
    } else {
        const file = document.getElementById("imageInput").files[0];
        if (!file) {
            alert("Upload image first");
            return;
        }
        formData.append("image", file);
    }

    try {
        const res = await fetch("http://127.0.0.1:5000/predict", {
            method: "POST",
            body: formData
        });

        const data = await res.json();

        if (!res.ok || data.error) {
            throw new Error(data.error || `HTTP ${res.status}`);
        }

        document.getElementById("emotion").innerText = data.emotion || "-";
        document.body.className = (data.emotion || "").toLowerCase();
        document.getElementById("confidence").innerText = "";

        showSongs(data.songs || []);

    } catch (err) {
        console.error("Predict error:", err);
        alert("Backend error. Check the Flask server console and ensure it is running.");
    }
}

function showSongs(songs) {
    const songsDiv = document.getElementById("songs");
    songsDiv.innerHTML = "";

    if (songs.length === 0) {
        songsDiv.innerHTML = "<div class='song'>No songs found</div>";
        return;
    }

    songs.forEach(song => {
        songsDiv.innerHTML += `
            <div class="song">
                <div class="song-title">${song.name}</div>
                <div class="song-artist">${song.artist}</div>

                <audio class="audio-player" controls>
                    <source src="${song.spotify_preview_url}" type="audio/mpeg">
                </audio>
            </div>
        `;
    });

    // 👇 IMPORTANT PART (control audio)
    const players = document.querySelectorAll(".audio-player");

    players.forEach(player => {
        player.addEventListener("play", () => {
            players.forEach(p => {
                if (p !== player) {
                    p.pause();
                    // p.currentTime = 0; // optional: reset
                }
            });
        });
    });

    players.forEach((player, index) => {
    player.addEventListener("ended", () => {
        if (players[index + 1]) {

            // wait 1 second before playing next
            setTimeout(() => {
                players[index + 1].play();
            }, 1500);

        }
    });
});
}
