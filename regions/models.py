import os
import pytz

from core.utils import sanitize_name
from datetime import datetime
from django.db import models

from cases.models import Case

def region_image_path(instance, filename):
    # region_folder = sanitize_name(instance.name)
    # return os.path.join(region_folder)
    pst = pytz.timezone('America/Los_Angeles')
    current_time = datetime.now(pst)
    timestamp = current_time.strftime("%Y%m%d-%H%M%S")
    filename = f"region_{ instance.region.id }.jpg"

    return os.path.join("cases", str(instance.case.id), "regions", filename)
    
class Region(models.Model):

    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="regions")
    time_stamp = models.DateTimeField()
    TL_x_in_frame = models.FloatField()
    TL_y_in_frame = models.FloatField()
    BR_x_in_frame =  models.FloatField()
    BR_y_in_frame = models.FloatField()
    group_id = models.IntegerField()

    def __str__(self):
        return f"Region: { self.id } - Case { self.case.name }"
    
    class Meta:
        indexes = [
            models.Index(fields=['case'])
        ]
    
class RegionImage(models.Model):

    region = models.OneToOneField(Region, on_delete=models.CASCADE, related_name="image")
    image = models.ImageField(upload_to=region_image_path, blank=True, null=True)

    def __str__(self):
        return f"Region Image { self.region.id }"
    
class RegionClassification(models.Model):

    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="classification")
    classification_score = models.FloatField()
    is_selected = models.BooleanField(default=False)
    classifier_id = models.IntegerField()

    def __str__(self):
        return f"Region { self.region.id } Classifcation { self.region_classification_score }"
        
    