from django.contrib import admin

from .models import Region, RegionImage, RegionClassification

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):

    list_display = ('id', 'get_case_id')
    search_fields = ('id', 'case__id')

    def get_case_id(self, obj):
        return obj.case_id
    get_case_id.short_description = 'Case ID'

@admin.register(RegionImage)
class RegionImageAdmin(admin.ModelAdmin):

    list_display = ('id', 'get_region_id', 'image')
    search_fields = ('id', 'region__id')

    def get_region_id(self, obj):
        return obj.region_id
    get_region_id.short_description = 'Region ID'

@admin.register(RegionClassification)
class RegionClassifcationAmdin(admin.ModelAdmin):

    list_display = ('id', 'get_region_id', 'classification_score', 'is_selected', 'classifier_id')
    search_fields = ('id', 'region__id', 'is_selected', 'classifier_id')

    def get_region_id(self, obj):
        return obj.region_id
    get_region_id.short_description = 'Region ID'