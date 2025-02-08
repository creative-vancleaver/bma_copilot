import os
import pytz

from datetime import datetime
from django.db import models

from regions.models import Region

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
    
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="cells")
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

    cell = models.OneToOneField(Cell, on_delete=models.CASCADE, related_name="detection")
    detection_score = models.FloatField(blank=True, null=True)
    model_id = models.CharField(max_length=100, blank=True, null=True)
    is_user_added = models.BooleanField(default=False)

    def __str__(self):
        return f"Detection for Cell { self.cell.id }"
    
class CellClassification(models.Model):

    cell = models.OneToOneField(Cell, on_delete=models.CASCADE, related_name='classification')
    ai_class = models.CharField(max_length=250, blank=True, null=True)
    user_class = models.CharField(max_length=250, blank=True, null=True)
    
    myelocyte_score = models.FloatField(blank=True, null=True)
    metamyelocyte_score = models.FloatField(blank=True, null=True)
    neutrophil_score = models.FloatField(blank=True, null=True)
    monocyte_score = models.FloatField(blank=True, null=True)
    eosinophil_score = models.FloatField(blank=True, null=True)
    erythroid_precursor_score = models.FloatField(blank=True, null=True)
    lymphocyte_score = models.FloatField(blank=True, null=True)
    plasma_cell_score = models.FloatField(blank=True, null=True)
    blast_score = models.FloatField(blank=True, null=True)
    skippocyte_score = models.FloatField(blank=True, null=True)

    model_id = models.CharField(max_length=100, blank=True, null=True)

    basophil_score = models.FloatField(blank=True, null=True)


    def __str__(self):
        return f"Cell { self.cell.id } Classification"