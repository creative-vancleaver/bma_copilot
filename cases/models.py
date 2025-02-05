import os
from django.db import models

from core.utils import sanitize_name
from users.models import User

def video_path(instance, filename):
    case_folder = sanitize_name(instance.name)
    return os.path.join(case_folder, 'videos', filename)

class Case(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]

    name = models.CharField(max_length=250)
    description = models.TextField(blank=True, null=True)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='pending')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cases')
    video_file_path = models.FileField(upload_to="video_path", blank=True, null=True)

    def __str__(self):
        return self.name