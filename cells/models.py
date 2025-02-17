import os
import pytz

from datetime import datetime
from django.db import models

from regions.models import Region
from users.models import CustomIDMixin

def cell_image_path(instance, filename):

    user_id = instance.region.video_id.case.user.user_id
    case_id = instance.region.case.id
    region_id = instance.region.id
    cell_id = instance.id

    filename = f"{user_id}_{case_id}_{region_id}_{cell_id}.jpg"

    return os.path.join(
        "cases", 
        str(instance.region.case.id), 
        "regions", 
        str(instance.region.id), 
        "cells", 
        filename
    )

class Cell(CustomIDMixin, models.Model):
    print("[DEBUG] Cell model is being loaded...")  # <-- Should print when Django loads the model  
    cell_id = models.CharField(primary_key=True, max_length=255, unique=True, default=None)
    cell_image_path = models.CharField(max_length=255, blank=True, null=True)
    region = models.ForeignKey(Region, db_column='region_id', to_field='region_id', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=cell_image_path, blank=True, null=True)
    center_x_in_region = models.FloatField(blank=True, null=True)
    center_y_in_region = models.FloatField(blank=True, null=True)
    TL_x_in_region = models.FloatField(blank=True, null=True)
    TL_y_in_region = models.FloatField(blank=True, null=True)
    BR_x_in_region = models.FloatField(blank=True, null=True)
    BR_y_in_region = models.FloatField(blank=True, null=True)

    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.cell_id
    
    def save(self, *args, **kwargs):
        if not self.cell_id:
            self.cell_id = self.generate_custom_id(region_id=self.region.region_id)

        super().save(*args, **kwargs)

    class Meta:
        # managed = False
        db_table = 'cells'
        indexes = [
            models.Index(fields=['region'])
        ]
    
class CellDetection(models.Model):

    cell = models.OneToOneField(Cell, db_column='cell_id', to_field='cell_id', primary_key=True, on_delete=models.CASCADE)
    cell_detection_score = models.FloatField(blank=True, null=True)
    model_id = models.CharField(max_length=100, db_column='cell_detection_model_id', blank=True, null=True)
    is_user_added = models.BooleanField(default=False)

    def __str__(self):
        return self.cell.cell_id
    
    class Meta:
        # managed = False
        db_table = 'cell_detection'  # Match Azure table name
    
class CellClassification(models.Model):
    cell = models.OneToOneField(Cell, db_column='cell_id', to_field='cell_id', primary_key=True, on_delete=models.CASCADE)

    ai_cell_class = models.CharField(max_length=250, blank=True, null=True)
    user_cell_class = models.CharField(max_length=250, blank=True, null=True)

    # Classification Scores
    myelocytes_score = models.FloatField(blank=True, null=True)
    metamyelocytes_score = models.FloatField(blank=True, null=True)
    monocytes_score = models.FloatField(blank=True, null=True)
    eosinophils_score = models.FloatField(blank=True, null=True)
    erythroid_precursors_score = models.FloatField(blank=True, null=True)
    lymphocytes_score = models.FloatField(blank=True, null=True)
    plasma_cells_score = models.FloatField(blank=True, null=True)
    skippocyte_score = models.FloatField(blank=True, null=True)
    blasts_and_blast_equivalents_score = models.FloatField(blank=True, null=True)
    neutrophils_bands_score = models.FloatField(blank=True, null=True)

    cell_classification_model_id = models.CharField(max_length=255, blank=True, null=True)  # Make nullable

    def __str__(self):
        return self.cell.cell_id

    class Meta:
        # managed = False
        db_table = 'cell_classification'  # Match Azure table name
        indexes = [
            models.Index(fields=['cell']),
        ]