from django.contrib import admin

from .models import Case, Video
from users.models import User

@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):

    list_display = ('case_id', 'case_name', 'get_user_email', 'case_date', 'case_status')
    search_fields = ('case_id', 'case_name', 'case_description', 'user__email')

    def get_user_email(self, obj):
        return obj.user.email if obj.user else None
    get_user_email.short_description = 'User Email'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'user':
            kwargs['queryset'] = User.objects.all().order_by('email')
            kwargs['to_field_name'] = 'user_id' 
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):

    list_display = ('get_case_id', 'video_file_path', 'azure_url', 'date_added')
    search_fields = ('case_id',)

    def get_case_id(self, obj):
        return obj.case_id
    get_case_id.short_description = 'Case ID'
