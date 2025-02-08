import os
import pytz

from datetime import datetime
from django.db import models

from core.utils import sanitize_name
from users.models import User

def case_video_path(instance, filename):

    pst = pytz.timezone('America/Los_Angeles')
    current_time = datetime.now(pst)
    timestamp = current_time.strftime("%Y%m%d-%H%M%S")

    filename = f"recording_{ timestamp }.webm"

    return os.path.join("cases", str(instance.case.id), "recordings", filename)

class Case(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]

    name = models.CharField(max_length=250)
    date_added = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='pending')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cases')

    def __str__(self):
        return self.name
    
    class Meta:
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['date']), 
            models.Index(fields=['user'])
        ]

class Video(models.Model):

    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="videos")
    video_file = models.FileField(upload_to=case_video_path, blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Video for Case: { self.case.name }"