import os
import pytz

from core.utils import sanitize_name
from datetime import datetime
from django.db import models

from cases.models import Case, Video

def region_image_path(instance, filename):
    # region_folder = sanitize_name(instance.name)
    # return os.path.join(region_folder)
    pst = pytz.timezone('America/Los_Angeles')
    current_time = datetime.now(pst)
    timestamp = current_time.strftime("%Y%m%d-%H%M%S")
    filename = f"region_{ instance.region.id }.jpg"

    return os.path.join("cases", str(instance.region.case.id), "regions", str(instance.region.id), filename)
    
class Region(models.Model):

    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="regions")
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='regions', blank=True, null=True)
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

    region = models.OneToOneField(Region, on_delete=models.CASCADE, related_name="image")
    image = models.ImageField(upload_to=region_image_path, blank=True, null=True)

    def __str__(self):
        return f"Region Image { self.region.id }"
    
class RegionClassification(models.Model):

    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="classification")
    classification_score = models.FloatField(blank=True, null=True)
    is_selected = models.BooleanField(default=False)
    classifier_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"Region { self.region.id } Classification { self.region_classification_score }"
        
    