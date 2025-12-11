// ==============================
// DOM REFERENCES
// ==============================
const img = document.getElementById("toshi-img");
const video = document.getElementById("toshi-video");
const chat = document.getElementById("chat");
const audio = document.getElementById("toshi-voice");
const toshiBtn = document.getElementById("toshi-btn");

let toshiMode = false;
let isWaitingForAudio = false;


// ==============================
// Add message to chat
// ==============================
function addMessage(msg) {
    chat.innerHTML = "<p>" + msg + "</p>";
}


// ==============================
// Toggle Toshi Mode
// ==============================
function toggleToshiMode() {
    fetch("/api/toshi_mode", { method: "POST" })
        .then(r => r.json())
        .then(data => {
            toshiMode = data.toshi_mode;

            if (toshiMode) {
                img.style.display = "none";
                video.style.display = "block";

                video.currentTime = 0;
                video.muted = true;
                video.play().catch(() => {
                    video.muted = true;
                    video.play();
                });

                toshiBtn.innerText = "Toshi Mode On";

            } else {
                video.pause();
                video.style.display = "none";
                img.style.display = "block";

                toshiBtn.innerText = "Toshi Mode Off";
            }
        })
        .catch(err => console.error("Toggle error:", err));
}



// ==============================
// Main Convert Function
// ==============================
async function convert() {
    const amount = parseFloat(document.getElementById("usd-input").value);

    if (!amount) {
        addMessage("Please enter an amount first 💗");
        return;
    }

    if (isWaitingForAudio) return;

    const payload = { amount, toshi_mode: toshiMode };

    try {
        const res = await fetch("/api/convert", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const data = await res.json();

        addMessage(`
            USD → JPY: ¥${data.jpy.toFixed(2)}<br>
            Toshi price: $${data.toshi_price}<br>
            Coins you'd get: ${data.toshi_amount.toFixed(4)} 🪙<br><br>
            💗 Toshi-chan: ${data.ai_reply}
        `);

        if (toshiMode) {
            isWaitingForAudio = true;

            // Fetch TTS audio
            const ttsRes = await fetch("/api/tts", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text: data.ai_reply })
            });

            const blob = await ttsRes.blob();
            const audioUrl = URL.createObjectURL(blob);

            // Use ONLY the HTML audio element
            audio.src = audioUrl;
            audio.autoplay = true;
            audio.muted = false;

            audio.play().catch(err => {
                console.warn("Autoplay blocked, retrying:", err);
                audio.play();
            });
        }

    } catch (err) {
        console.error("Convert error:", err);
        addMessage("Something went wrong 💔");
    }
}


// ==============================
// Speak Function (manual voice trigger)
// ==============================
async function speak(text) {
    const res = await fetch("/api/tts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text })
    });

    const blob = await res.blob();
    const audioUrl = URL.createObjectURL(blob);

    console.log("TTS Blob:", blob);
    console.log("Blob type:", blob.type);

    audio.src = audioUrl;
    audio.autoplay = true;
    audio.muted = false;

    audio.play().catch(err => {
        console.warn("Autoplay blocked:", err);
        audio.play();
    });
}


// ==============================
// When TTS ends, allow refresh
// ==============================
audio.addEventListener("ended", () => {
    isWaitingForAudio = false;

    if (toshiMode) {
        convert();
    }
});
