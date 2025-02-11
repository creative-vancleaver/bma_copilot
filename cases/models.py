import os
import pytz

from datetime import datetime
from django.db import models

from core.utils import sanitize_name
from users.models import User, CustomIDMixin

def case_video_path(instance, filename):

    pst = pytz.timezone('America/Los_Angeles')
    current_time = datetime.now(pst)
    timestamp = current_time.strftime("%Y%m%d-%H%M%S")

    user_id = instance.case.user.id
    case_id = instance.case.id
    video_id = instance.id

    # filename = f"recording_{ timestamp }.webm"
    filename = f"{user_id}_{case_id}_{video_id}.webm"

    return os.path.join("cases", str(instance.case.id), "recordings", filename)

class Case(CustomIDMixin, models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]

    # case_id = models.CharField(primary_key=True, max_length=255)
    # name = models.CharField(max_length=250)
    # date_added = models.DateTimeField(auto_now_add=True)
    # description = models.TextField(blank=True, null=True)
    # date = models.DateField()
    # time = models.TimeField()
    # status = models.CharField(choices=STATUS_CHOICES, max_length=25, default='pending')
    # user = models.ForeignKey(User, db_column='user_id', to_field='id', on_delete=models.CASCADE)

    case_id = models.CharField(primary_key=True, max_length=255, unique=True, default=CustomIDMixin.generate_custom_id)
    case_name = models.CharField(max_length=255, blank=True, null=True)
    case_description = models.TextField(blank=True, null=True)  # This field type is a guess.
    case_date = models.DateField(blank=True, null=True)
    case_time = models.TimeField(blank=True, null=True)
    case_status = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey(User, db_column='user_id', to_field='user_id', on_delete=models.CASCADE)

    def __str__(self):
        return self.case_name
    
    class Meta:
        # managd = False
        db_table = 'cases'
        indexes = [
            models.Index(fields=['case_status']),
            models.Index(fields=['user'])
        ]

class Video(CustomIDMixin, models.Model):

    video_id = models.CharField(primary_key=True, max_length=255, unique=True, default=CustomIDMixin.generate_custom_id)
    video_file_path = models.CharField(max_length=255, blank=True, null=True)
    case = models.ForeignKey(Case, on_delete=models.CASCADE, db_column='case_id')

    # video_id = models.CharField(primary_key=True, max_length=255)
    # case = models.ForeignKey(Case, db_column='case_id', to_field='case_id', on_delete=models.CASCADE)
    # video_file_path = models.CharField(max_length=255, blank=True, null=True)

    # video_file = models.FileField(upload_to=case_video_path, blank=True, null=True)
    # azure_url = models.URLField(max_length=500, blank=True, null=True) # TEMPORARY?
    # date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Video for Case: { self.case.case_name }"

    class Meta:
        # managd = False
        db_table = 'videos'