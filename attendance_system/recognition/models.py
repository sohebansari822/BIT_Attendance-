from django.db import models
import json

class Person(models.Model):
    name = models.CharField(max_length=100)
    employee_id = models.CharField(max_length=50, unique=True)
    # Store 512-dim ArcFace embedding as JSON text
    embedding = models.TextField()
    photo = models.ImageField(upload_to='persons/', blank=True, null=True)
    registered_at = models.DateTimeField(auto_now_add=True)

    def get_embedding(self):
        """Return embedding as numpy array"""
        import numpy as np
        return np.array(json.loads(self.embedding))

    def set_embedding(self, embedding_array):
        """Save numpy array as JSON"""
        self.embedding = json.dumps(embedding_array.tolist())

    def __str__(self):
        return f"{self.name} ({self.employee_id})"


class Attendance(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(auto_now_add=True)
    time_in = models.DateTimeField(auto_now_add=True)
    confidence = models.FloatField(default=0.0)  # similarity score

    class Meta:
        ordering = ['-time_in']
        # Prevent duplicate attendance on same day
        unique_together = ['person', 'date']

    def __str__(self):
        return f"{self.person.name} - {self.date}"
