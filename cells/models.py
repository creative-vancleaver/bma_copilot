import os
import pytz

from datetime import datetime
from django.db import models

from regions.models import Region

def cell_image_path(instance, filename):

    # pst = pytz.timezone('America/Los_Angeles')
    # current_time = datetime.now(pst)
    # timestamp = current_time.strftime("%Y%m%d-%H%M%S")
    # filename = f"cell_{ instance.id }.jpg"

    user_id = instance.region.case.user.id
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

class Cell(models.Model):
    cell_id = models.CharField(primary_key=True, max_length=255)
    cell_image_path = models.CharField(max_length=255, blank=True, null=True)
    region = models.ForeignKey(Region, db_column='region_id', to_field='region_id', on_delete=models.CASCADE)
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
        # managd = False
        db_table = 'cells'
        indexes = [
            models.Index(fields=['region'])
        ]
    
class CellDetection(models.Model):

    cell = models.OneToOneField(Cell, db_column='cell_id', to_field='cell_id', primary_key=True, on_delete=models.CASCADE)
    detection_score = models.FloatField(blank=True, null=True)
    model_id = models.CharField(max_length=100, blank=True, null=True)
    is_user_added = models.BooleanField(default=False)

    def __str__(self):
        return f"Detection for Cell { self.cell.id }"
    
    class Meta:
        # managd = False
        db_table = 'cell_detection'  # Match Azure table name
    
class CellClassification(models.Model):
    cell = models.OneToOneField(Cell, db_column='cell_id', to_field='cell_id', primary_key=True, on_delete=models.CASCADE)    # Make all fields nullable except primary relationships

    ai_class = models.CharField(max_length=250, blank=True, null=True)
    user_class = models.CharField(max_length=250, blank=True, null=True)

    # Classification Scores
    myelocyte_score = models.FloatField(blank=True, null=True)
    metamyelocyte_score = models.FloatField(blank=True, null=True)
    monocyte_score = models.FloatField(blank=True, null=True)
    eosinophil_score = models.FloatField(blank=True, null=True)
    erythroid_precursor_score = models.FloatField(blank=True, null=True)
    lymphocyte_score = models.FloatField(blank=True, null=True)
    plasma_cell_score = models.FloatField(blank=True, null=True)
    skippocyte_score = models.FloatField(blank=True, null=True)
    blasts_and_blast_equivalents_score = models.FloatField(blank=True, null=True)
    neutrophils_bands_score = models.FloatField(blank=True, null=True)

    cell_classification_model_id = models.CharField(max_length=255, blank=True, null=True)  # Make nullable

    # neutrophil_score = models.FloatField(blank=True, null=True)
    # basophil_score = models.FloatField(blank=True, null=True)
    # blast_score = models.FloatField(blank=True, null=True)


    def __str__(self):
        return f"Cell { self.cell.id } Classification"

    class Meta:
        # managd = False
        db_table = 'cell_classification'  # Match Azure table name