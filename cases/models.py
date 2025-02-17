import os
import pytz

from datetime import datetime
from django.db import models, transaction, IntegrityError

from core.utils import sanitize_name
from users.models import User, CustomIDMixin

def case_video_path(instance, filename):

    user_id = instance.case.user.id
    case_id = instance.case.id
    video_id = instance.id

    filename = f"{user_id}_{case_id}_{video_id}.webm"

    return os.path.join("cases", str(instance.case.id), "recordings", filename)

class Case(CustomIDMixin, models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]

    case_id = models.CharField(
        primary_key=True, 
        max_length=255, 
        unique=True, 
        default=None
    )
    case_name = models.CharField(max_length=255, blank=True, null=True)
    case_description = models.TextField(blank=True, null=True)  # This field type is a guess.
    case_date = models.DateField(blank=True, null=True)
    case_time = models.TimeField(blank=True, null=True)
    case_status = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey(User, db_column='user_id', to_field='user_id', on_delete=models.CASCADE)

    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.case_id
    
    def save(self, *args, **kwargs):
        if not self.case_id:
            self.case_id = self.generate_custom_id(user_id=self.user.user_id)

        super().save(*args, **kwargs)
    
    class Meta:
        # managed = False
        db_table = 'cases'
        indexes = [
            models.Index(fields=['case_status']),
            models.Index(fields=['user'])
        ]

class Video(CustomIDMixin, models.Model):

    video_id = models.CharField(
        primary_key=True, 
        max_length=255, 
        unique=True,
        default=None    
    )
    video_file_path = models.CharField(max_length=255, blank=True, null=True)
    case = models.ForeignKey(Case, on_delete=models.CASCADE, db_column='case_id')
    TL_x = models.FloatField(blank=True, null=True)
    TL_y = models.FloatField(blank=True, null=True)
    BR_x = models.FloatField(blank=True, null=True)
    BR_y = models.FloatField(blank=True, null=True)

    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.video_id
    
    def save(self, *args, **kwargs):
        
        if not self.video_id:
            self.video_id = self.generate_custom_id(case_id=self.case.case_id)

            print(f"[DEBUG] Assigning Video ID: {self.video_id}")

        super().save(*args, **kwargs)
    
    class Meta:
        # managed = False
        db_table = 'videos'