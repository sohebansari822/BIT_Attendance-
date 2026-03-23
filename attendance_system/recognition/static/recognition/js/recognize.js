/* ─── recognize.js ───────────────────────────────────────────────── */

const video      = document.getElementById('video');
const canvas     = document.getElementById('canvas');
const captureBtn = document.getElementById('captureBtn');
const resultCard = document.getElementById('resultCard');

// ─── Camera ────────────────────────────────────────────────────────
navigator.mediaDevices.enumerateDevices().then(devices => {
  const cameras = devices.filter(d => d.kind === 'videoinput');
  const cam = cameras[1] || cameras[0];
  return navigator.mediaDevices.getUserMedia({
    video: { deviceId: { exact: cam.deviceId }, width: 640, height: 480 }
  });
}).then(stream => {
  video.srcObject = stream;
}).catch(e => {
  resultCard.innerHTML = `<p class="result-error">Camera error: ${e.message}</p>`;
});

// ─── Capture & Recognize ───────────────────────────────────────────
captureBtn.addEventListener('click', async () => {
  canvas.width  = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext('2d').drawImage(video, 0, 0);
  const imageData = canvas.toDataURL('image/jpeg', 0.9);

  captureBtn.disabled  = true;
  captureBtn.innerHTML = '<span class="spinner"></span>Recognizing...';
  resultCard.innerHTML = `
    <div class="spinner spinner-large"></div>
    <p class="result-confidence">Analyzing face...</p>
  `;

  try {
    const res  = await fetch('/recognize/submit/', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ image: imageData })
    });
    const data = await res.json();

    if (data.success) {
      const colorClass = data.already_marked ? 'result-warning' : 'result-success';
      const icon       = data.already_marked ? '⚠️' : '✅';
      resultCard.innerHTML = `
        <div class="result-icon">${icon}</div>
        <div class="result-message ${colorClass}">${data.message}</div>
        <div class="result-confidence">Confidence: ${(data.score * 100).toFixed(1)}%</div>
      `;
      loadTodayList();
    } else {
      resultCard.innerHTML = `
        <div class="result-icon">❌</div>
        <div class="result-message result-error">${data.error}</div>
      `;
    }
  } catch (e) {
    resultCard.innerHTML = `<div class="result-error">Network error: ${e.message}</div>`;
  }

  captureBtn.disabled  = false;
  captureBtn.innerHTML = '📸 Capture & Recognize';
});

// ─── Today's List ──────────────────────────────────────────────────
async function loadTodayList() {
  document.getElementById('todayList').innerHTML = `
    <p class="today-empty">
      Updated! <a href="/attendance/">View full records →</a>
    </p>
  `;
}

loadTodayList();
