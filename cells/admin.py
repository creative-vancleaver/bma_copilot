from django.contrib import admin

from .models import Cell, CellDetection, CellClassification

@admin.register(Cell)
class CellAdmin(admin.ModelAdmin):

    list_display = ('cell_id', 'get_region_id', 'get_case_id', 'date_added')
    search_fields = ('cell_id', 'region__region_id')

    def get_region_id(self, obj):
        return obj.region.region_id
    get_region_id.short_description = "Region ID"
    get_region_id.admin_order_field = 'region__region_id'

    def get_case_id(self, obj):
        if obj.region is not None:
            return obj.region.video_id.case.case_id
        return None
    get_case_id.short_description = 'Case ID'
    get_case_id.admin_order_field = 'region__case__case_id'

@admin.register(CellDetection)
class CellDetectionAdmin(admin.ModelAdmin):

    list_display = ('get_cell_id', 'cell_detection_score', 'model_id', 'is_user_added')
    search_fields = ('cell__cell_id',)

    def get_cell_id(self, obj):
        return obj.cell.cell_id
    get_cell_id.short_description = 'Cell ID'
    get_cell_id.admin_order_field = 'cell__cell_id'

@admin.register(CellClassification)
class CellClassificationAdmin(admin.ModelAdmin):

    list_display = ('get_cell_id', 'ai_cell_class', 'user_cell_class', 'cell_classification_model_id')
    search_fields = ('cell__cell_id', 'cell_classification_model_id', 'user_cell_class', 'ai_cell_class')

    def get_cell_id(self, obj):
        return obj.cell.cell_id
    get_cell_id.short_description = 'Cell ID'
    get_cell_id.admin_order_field = 'cell__cell_id'
