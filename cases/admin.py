from django.contrib import admin

from .models import Case, Video

@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):

    list_display = ('name', 'date', 'status')
    search_fields = ('name', 'description')

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):

    list_display = ('case_id', 'video_file', 'date_added')
    search_fields = ('case_id',)

    def get_case_id(self, obj):
        return obj.case_id
    get_case_id.short_description = 'Case ID'
