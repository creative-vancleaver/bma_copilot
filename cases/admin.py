from django.contrib import admin

from .models import Case, Video

@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):

    list_display = ('case_id', 'case_name', 'case_date', 'case_status')
    search_fields = ('case_id', 'case_name', 'case_description')

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):

    list_display = ('get_case_id', 'video_file', 'date_added')
    search_fields = ('case_id',)

    def get_case_id(self, obj):
        return obj.case_id
    get_case_id.short_description = 'Case ID'
