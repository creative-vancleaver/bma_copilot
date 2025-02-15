from django.contrib import admin

from .models import Region, RegionImage, RegionClassification

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):

    list_display = ('region_id', 'get_video_id')
    search_fields = ('region_id', 'video_id__video_id')

    def get_video_id(self, obj):
        return obj.video_id.video_id if obj.video_id else None
    get_video_id.short_description = 'Video ID'
    get_video_id.admin_order_field = 'video_id__video_id'

@admin.register(RegionImage)
class RegionImageAdmin(admin.ModelAdmin):

    list_display = ('get_region_id', 'image')
    search_fields = ('region__region_id',)

    def get_region_id(self, obj):
        return obj.region_id
    get_region_id.short_description = 'Region ID'

@admin.register(RegionClassification)
class RegionClassificationAdmin(admin.ModelAdmin):

    list_display = ('region_id', 'get_region_id', 'region_classification_score', 'is_selected_by_region_classifier', 'region_classifier_id')
    search_fields = ('region_id', 'region__region_id', 'is_selected_by_region_classifier', 'region_classifier_id')

    def get_region_id(self, obj):
        return obj.region_id
    get_region_id.short_description = 'Region ID'