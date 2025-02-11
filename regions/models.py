import os
import pytz

from core.utils import sanitize_name
from datetime import datetime
from django.db import models

from cases.models import Case, Video
from users.models import CustomIDMixin

def region_image_path(instance, filename):
    # region_folder = sanitize_name(instance.name)
    # return os.path.join(region_folder)
    # pst = pytz.timezone('America/Los_Angeles')
    # current_time = datetime.now(pst)
    # timestamp = current_time.strftime("%Y%m%d-%H%M%S")
    # filename = f"region_{ instance.region.id }.jpg"
    user_id = instance.region.case.user.id
    case_id = instance.region.case.id
    region_id = instance.region.id

    filename = f"{user_id}_{case_id}_{region_id}.jpg"

    return os.path.join("cases", str(instance.region.case.id), "regions", str(instance.region.id), filename)
    
class Region(CustomIDMixin, models.Model):
    region_id = models.CharField(primary_key=True, max_length=255, unique=True, default=CustomIDMixin.generate_custom_id)  # Match Azure's region_id
    case = models.ForeignKey(Case, db_column='case_id', to_field='case_id', on_delete=models.CASCADE, related_name="regions", blank=True, null=True)
    video_id = models.ForeignKey(Video, db_column='video_id', to_field='video_id', on_delete=models.CASCADE, null=True, blank=True)
    time_stamp = models.DateTimeField(blank=True, null=True)
    TL_x_in_frame = models.FloatField(blank=True, null=True)
    TL_y_in_frame = models.FloatField(blank=True, null=True)
    BR_x_in_frame = models.FloatField(blank=True, null=True)
    BR_y_in_frame = models.FloatField(blank=True, null=True)

    group_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"Region: { self.id } - Case { self.case.name }"
    
    class Meta:
        # managd = False
        db_table = 'region'  # Match Azure table name (note: singular as per your schema)
        indexes = [
            models.Index(fields=['case']),
            models.Index(fields=['video_id'])
        ]
    
class RegionImage(models.Model):
    region_id = models.OneToOneField(Region, db_column='region_id', to_field='region_id', primary_key=True, on_delete=models.CASCADE)
    region_image_path = models.CharField(max_length=255, blank=True, null=True)  # Make nullable
    image = models.ImageField(upload_to=region_image_path, blank=True, null=True)

    def __str__(self):
        return f"Region Image { self.region.id }"
    
    class Meta:
        # managd = False
        db_table = 'region_image_selected'  # Match Azure table name
    
class RegionClassification(models.Model):

    region_id = models.OneToOneField(
        Region, db_column='region_id', to_field='region_id',
        primary_key=True, on_delete=models.CASCADE
    )
    region_classification_score = models.FloatField(blank=True, null=True)
    is_selected_by_region_classifier = models.BooleanField(default=False)
    region_classifier_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Region { self.region.id } Classification { self.region_classification_score }"
        
    class Meta:
        # managd = False
        db_table = 'region_classification'  # Match Azure table name
    