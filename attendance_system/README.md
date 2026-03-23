🎓 BIT-Attendance — Face Recognition Attendance System

## Tech Stack
- **Django** — Web framework + SQLite database
- **MTCNN** — Face detection & alignment (via DeepFace)
- **ArcFace** — 512-dim face embedding (via DeepFace)
- **Cosine Similarity** — Identity matching

---

## ✅ Step-by-Step Setup Guide

### STEP 1 — Install Python
Make sure Python 3.9 or 3.10 is installed.
Check: `python --version`
Download from: https://python.org/downloads

---

### STEP 2 — Create a Virtual Environment
Open terminal/command prompt in this folder:

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate
```

You should see `(venv)` at the start of your terminal prompt.

---

### STEP 3 — Install Dependencies
```bash
pip install -r requirements.txt
```

This will install Django, DeepFace, OpenCV, and all required packages.
⚠️ First time takes 5–10 minutes. ArcFace model (~250MB) downloads automatically on first run.

---

### STEP 4 — Set Up the Database
```bash
python manage.py makemigrations
python manage.py migrate
```

This creates `db.sqlite3` with all required tables.

---

### STEP 5 — Run the Server
```bash
python manage.py runserver
```

You should see:
```
Starting development server at http://127.0.0.1:8000/
```

---

### STEP 6 — Open in Browser
Go to: **http://127.0.0.1:8000**

---

## 📖 How to Use

### Register a Person
1. Click **Register** in the navbar
2. Enter the person's Name and Employee ID
3. Click **Capture Photo** (allow camera access when prompted)
4. Click **Register Person**

### Mark Attendance
1. Click **Mark Attendance** in the navbar
2. Face the camera
3. Click **Capture & Recognize**
4. System will identify the person and log attendance

### View Records
1. Click **Records** in the navbar
2. Filter by date using the date picker

---

## 🔧 Configuration

Edit `attendance_system/settings.py` to change:
```python
FACE_MATCH_THRESHOLD = 0.68  # increase for stricter matching (0.0 to 1.0)
```

---

## ❓ Common Issues

| Problem | Fix |
|---|---|
| Camera not working | Allow browser camera permission, use Chrome/Edge |
| "No face detected" | Ensure good lighting, face camera directly |
| Slow first recognition | Normal — ArcFace model loads on first use (~30 seconds) |
| ModuleNotFoundError | Make sure virtual environment is activated |
| Port already in use | Use `python manage.py runserver 8001` |

---

## 📁 Project Structure
```
attendance_system/
├── manage.py               # Django entry point
├── requirements.txt        # Python dependencies
├── db.sqlite3              # SQLite database (auto-created)
├── attendance_system/
│   ├── settings.py         # Django settings
│   └── urls.py             # Main URL routing
└── recognition/
    ├── models.py           # Person & Attendance DB models
    ├── views.py            # All HTTP handlers
    ├── face_utils.py       # MTCNN + ArcFace logic
    ├── urls.py             # App URL routing
    └── templates/          # HTML pages
```
