/* ─── register.js ────────────────────────────────────────────────── */

const video        = document.getElementById('video');
const canvas       = document.getElementById('canvas');
const captureBtn   = document.getElementById('captureBtn');
const retakeBtn    = document.getElementById('retakeBtn');
const preview      = document.getElementById('preview');
const previewWrap  = document.getElementById('preview-container');
const submitBtn    = document.getElementById('submitBtn');
const alertBox     = document.getElementById('alertBox');
const modal        = document.getElementById('deleteModal');

let capturedImage  = null;
let deleteTargetId = null;

// ─── Camera ────────────────────────────────────────────────────────
navigator.mediaDevices.enumerateDevices().then(devices => {
  const cameras = devices.filter(d => d.kind === 'videoinput');
  const cam = cameras[1] || cameras[0];
  return navigator.mediaDevices.getUserMedia({
    video: { deviceId: { exact: cam.deviceId }, width: 640, height: 480 }
  });
}).then(stream => {
  video.srcObject = stream;
}).catch(e => showAlert('Camera error: ' + e.message, 'error'));

captureBtn.addEventListener('click', () => {
  canvas.width  = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext('2d').drawImage(video, 0, 0);
  capturedImage = canvas.toDataURL('image/jpeg', 0.9);
  preview.src   = capturedImage;
  previewWrap.classList.remove('hidden');
  video.style.display        = 'none';
  captureBtn.style.display   = 'none';
  retakeBtn.style.display    = 'inline-block';
  submitBtn.disabled         = false;
  hideAlert();
});

retakeBtn.addEventListener('click', () => {
  capturedImage = null;
  previewWrap.classList.add('hidden');
  video.style.display        = 'block';
  captureBtn.style.display   = 'inline-block';
  retakeBtn.style.display    = 'none';
  submitBtn.disabled         = true;
  hideAlert();
});

// ─── Register Submit ───────────────────────────────────────────────
submitBtn.addEventListener('click', async () => {
  const name        = document.getElementById('name').value.trim();
  const employee_id = document.getElementById('employee_id').value.trim();

  if (!name || !employee_id) { showAlert('Please fill in all fields.', 'error'); return; }
  if (!capturedImage)        { showAlert('Please capture a photo first.', 'error'); return; }

  submitBtn.disabled   = true;
  submitBtn.innerHTML  = '<span class="spinner"></span>Processing...';

  try {
    const res  = await fetch('/register/submit/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, employee_id, image: capturedImage })
    });
    const data = await res.json();

    if (data.success) {
      showAlert(data.message, 'success');
      document.getElementById('name').value        = '';
      document.getElementById('employee_id').value = '';
      retakeBtn.click();
      loadPersons();
    } else {
      showAlert(data.error, 'error');
    }
  } catch (e) {
    showAlert('Network error: ' + e.message, 'error');
  }

  submitBtn.disabled  = false;
  submitBtn.innerHTML = '✅ Register Person';
});

// ─── Persons Table ─────────────────────────────────────────────────
async function loadPersons() {
  const res  = await fetch('/register/persons/');
  const data = await res.json();
  const tbody = document.getElementById('personTableBody');
  document.getElementById('personCount').textContent = data.persons.length + ' registered';

  if (data.persons.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5" class="table-empty">No persons registered yet.</td></tr>';
    return;
  }

  tbody.innerHTML = data.persons.map((p, i) => `
    <tr id="row-${p.id}">
      <td class="muted">${i + 1}</td>
      <td><strong>${p.name}</strong></td>
      <td><span class="badge badge-blue">${p.employee_id}</span></td>
      <td class="muted">${p.registered_at}</td>
      <td>
        <button class="btn btn-danger" style="padding:0.35rem 0.9rem;font-size:0.8rem"
          onclick="openDeleteModal(${p.id}, '${p.name}')">
          🗑 Delete
        </button>
      </td>
    </tr>
  `).join('');
}

// ─── Delete Modal ──────────────────────────────────────────────────
function openDeleteModal(id, name) {
  deleteTargetId = id;
  document.getElementById('deleteName').textContent = name;
  modal.classList.add('open');
}

document.getElementById('cancelDeleteBtn').addEventListener('click', () => {
  modal.classList.remove('open');
  deleteTargetId = null;
});

document.getElementById('confirmDeleteBtn').addEventListener('click', async () => {
  if (!deleteTargetId) return;
  const btn = document.getElementById('confirmDeleteBtn');
  btn.disabled   = true;
  btn.innerHTML  = '<span class="spinner"></span>Deleting...';

  try {
    const res  = await fetch(`/register/delete/${deleteTargetId}/`, { method: 'POST' });
    const data = await res.json();
    modal.classList.remove('open');

    if (data.success) {
      showAlert(data.message, 'success');
      loadPersons();
    } else {
      showAlert(data.error, 'error');
    }
  } catch (e) {
    showAlert('Network error: ' + e.message, 'error');
  }

  btn.disabled  = false;
  btn.innerHTML = 'Yes, Delete';
  deleteTargetId = null;
});

// ─── Helpers ───────────────────────────────────────────────────────
function showAlert(msg, type) {
  alertBox.className   = 'alert alert-' + type;
  alertBox.textContent = msg;
}

function hideAlert() {
  alertBox.className = 'hidden';
}

// Load table on page open
loadPersons();
