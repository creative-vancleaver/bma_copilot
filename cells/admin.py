from django.contrib import admin

from .models import Cell, CellDetection, CellClassification

@admin.register(Cell)
class CellAdmin(admin.ModelAdmin):

    list_display = ('id', 'get_region_id', 'image')
    search_fields = ('id', 'region__id')

    def get_region_id(self, obj):
        return obj.region_id
    get_region_id.short_description = "Region ID"

@admin.register(CellDetection)
class CellDetectionAdmin(admin.ModelAdmin):

    list_display = ('id', 'get_cell_id', 'detection_score', 'model_id', 'is_user_added')
    search_fields = ('id', 'cell__id')

    def get_cell_id(self, obj):
        return obj.cell_id
    get_cell_id.short_description = 'Cell ID'

@admin.register(CellClassification)
class CellClassificationAdmin(admin.ModelAdmin):

    list_display = ('id', 'get_cell_id', 'ai_class', 'user_class', 'model_id')
    search_fields = ('id', 'cell__id', 'model_id')

    def get_cell_id(self, obj):
        return obj.cell_id
    get_cell_id.short_description = 'Cell ID'