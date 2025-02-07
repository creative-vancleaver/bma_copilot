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

    return os.path.join("cases", str(instance.id), "recordings", filename)

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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='core_cases')
    video_file = models.FileField(upload_to=case_video_path, blank=True, null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['date']), 
            models.Index(fields=['user'])
        ]


def region_image_path(instance, filename):
    # region_folder = sanitize_name(instance.name)
    # return os.path.join(region_folder)
    pst = pytz.timezone('America/Los_Angeles')
    current_time = datetime.now(pst)
    timestamp = current_time.strftime("%Y%m%d-%H%M%S")
    filename = f"region_{ instance.region.id }.jpg"

    return os.path.join("cases", str(instance.region.case.id), "regions", str(instance.region.id), filename)
    
class Region(models.Model):

    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="core_regions")
    time_stamp = models.DateTimeField(blank=True, null=True)
    TL_x_in_frame = models.FloatField(blank=True, null=True)
    TL_y_in_frame = models.FloatField(blank=True, null=True)
    BR_x_in_frame =  models.FloatField(blank=True, null=True)
    BR_y_in_frame = models.FloatField(blank=True, null=True)
    group_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"Region: { self.id } - Case { self.case.name }"
    
    class Meta:
        indexes = [
            models.Index(fields=['case'])
        ]
    
class RegionImage(models.Model):

    region = models.OneToOneField(Region, on_delete=models.CASCADE, related_name="core_image")
    image = models.ImageField(upload_to=region_image_path, blank=True, null=True)

    def __str__(self):
        return f"Region Image { self.region.id }"
    
class RegionClassification(models.Model):

    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="core_classification")
    classification_score = models.FloatField(blank=True, null=True)
    is_selected = models.BooleanField(default=False)
    classifier_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"Region { self.region.id } Classification { self.region_classification_score }"


def cell_image_path(instance, filename):

    pst = pytz.timezone('America/Los_Angeles')
    current_time = datetime.now(pst)
    timestamp = current_time.strftime("%Y%m%d-%H%M%S")
    filename = f"cell_{ instance.id }.jpg"

    return os.path.join(
        "cases", 
        str(instance.region.case.id), 
        "regions", 
        str(instance.region.id), 
        "cells", 
        filename
    )

class Cell(models.Model):
    
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="core_cells")
    image = models.ImageField(upload_to=cell_image_path, blank=True, null=True)
    center_x_in_region = models.FloatField(blank=True, null=True)
    center_y_in_region = models.FloatField(blank=True, null=True)
    TL_x_in_region = models.FloatField(blank=True, null=True)
    TL_y_in_region = models.FloatField(blank=True, null=True)
    BR_x_in_region = models.FloatField(blank=True, null=True)
    BR_y_in_region = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"Cell { self.id } in Region { self.region.id }"

    class Meta:
        indexes = [
            models.Index(fields=['region'])
        ]
    
class CellDetection(models.Model):

    cell = models.OneToOneField(Cell, on_delete=models.CASCADE, related_name="core_detection")
    detection_score = models.FloatField(blank=True, null=True)
    model_id = models.IntegerField(blank=True, null=True)
    is_user_added = models.BooleanField(default=False)

    def __str__(self):
        return f"Detection for Cell { self.cell.id }"
    
class CellClassification(models.Model):

    cell = models.OneToOneField(Cell, on_delete=models.CASCADE, related_name='core_classification')
    ai_class = models.CharField(max_length=250, blank=True, null=True)
    user_class = models.CharField(max_length=250, blank=True, null=True)
    
    blast_score = models.FloatField(blank=True, null=True)
    myelocyte_score = models.FloatField(blank=True, null=True)
    metamyelocyte_score = models.FloatField(blank=True, null=True)
    neutrophil_score = models.FloatField(blank=True, null=True)
    monocyte_score = models.FloatField(blank=True, null=True)
    eosinophil_score = models.FloatField(blank=True, null=True)
    basophil_score = models.FloatField(blank=True, null=True)
    lymphocyte_score = models.FloatField(blank=True, null=True)
    plasma_cell_score = models.FloatField(blank=True, null=True)
    erythroid_precursor_score = models.FloatField(blank=True, null=True)

    skippocyte_score = models.FloatField(blank=True, null=True)

    model_id = models.IntegerField()

    def __str__(self):
        return f"Cell { self.cell.id } Classification"
        
    