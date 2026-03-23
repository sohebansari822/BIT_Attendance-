"""
Face Recognition Utilities
--------------------------
Pipeline:
  Image → MTCNN (detect + align) → ArcFace (embedding) → Cosine Similarity → Match

Uses DeepFace library which internally uses:
  - MTCNN for face detection and alignment
  - ArcFace model for 512-dim feature embedding
"""

import numpy as np
import cv2
import base64
import logging
from deepface import DeepFace

logger = logging.getLogger(__name__)

# ─── Model warm-up ────────────────────────────────────────────────────────────
# DeepFace lazy-loads models on first call; we preload at startup
def warmup_models():
    """Pre-load MTCNN and ArcFace into memory to avoid first-call delay."""
    try:
        dummy = np.zeros((112, 112, 3), dtype=np.uint8)
        DeepFace.represent(
            img_path=dummy,
            model_name='ArcFace',
            detector_backend='mtcnn',
            enforce_detection=False
        )
        logger.info("✅ ArcFace + MTCNN models loaded successfully.")
    except Exception as e:
        logger.warning(f"Model warmup skipped: {e}")


# ─── Core Functions ────────────────────────────────────────────────────────────

def get_embedding(image_input):
    """
    Detect face using MTCNN, align it, then extract ArcFace embedding.

    Args:
        image_input: numpy array (BGR), file path string, or base64 string

    Returns:
        numpy array of shape (512,) — the face embedding
        None if no face detected
    """
    try:
        # Handle base64 string from browser webcam capture
        if isinstance(image_input, str) and image_input.startswith('data:image'):
            image_input = decode_base64_image(image_input)

        result = DeepFace.represent(
            img_path=image_input,
            model_name='ArcFace',        # ArcFace → 512-dim embedding
            detector_backend='mtcnn',    # MTCNN → detect + align face
            enforce_detection=True,
            align=True
        )

        if result and len(result) > 0:
            embedding = np.array(result[0]['embedding'])
            # L2 normalize for consistent cosine similarity
            embedding = embedding / np.linalg.norm(embedding)
            return embedding

    except Exception as e:
        logger.error(f"Face embedding failed: {e}")
        return None


def cosine_similarity(emb1, emb2):
    """
    Compute cosine similarity between two L2-normalized embeddings.
    Result is between 0 and 1. Higher = more similar.
    """
    return float(np.dot(emb1, emb2))


def find_best_match(query_embedding, all_persons, threshold=0.68):
    """
    Compare query embedding against all stored person embeddings.
    Uses cosine similarity.

    Args:
        query_embedding: 512-dim numpy array
        all_persons: QuerySet of Person model objects
        threshold: minimum similarity to count as a match

    Returns:
        (Person object, similarity_score) or (None, 0.0) if no match
    """
    best_person = None
    best_score = 0.0

    for person in all_persons:
        stored_embedding = person.get_embedding()
        score = cosine_similarity(query_embedding, stored_embedding)

        if score > best_score:
            best_score = score
            best_person = person

    if best_score >= threshold:
        return best_person, best_score

    return None, best_score


# ─── Helper Functions ──────────────────────────────────────────────────────────

def decode_base64_image(base64_string):
    """Convert base64 image string (from browser) to numpy array."""
    # Remove header e.g. "data:image/jpeg;base64,..."
    if ',' in base64_string:
        base64_string = base64_string.split(',')[1]

    img_bytes = base64.b64decode(base64_string)
    img_array = np.frombuffer(img_bytes, dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    return img


def save_face_image(image_np, save_path):
    """Save a numpy BGR image to disk."""
    cv2.imwrite(save_path, image_np)
