from django.apps import AppConfig

class RecognitionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recognition'

    def ready(self):
        """Pre-load ArcFace + MTCNN models when Django starts."""
        try:
            from .face_utils import warmup_models
            warmup_models()
        except Exception:
            pass
