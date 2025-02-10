from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):

    list_display = ('user_id', 'email', 'institution', 'is_staff')
    search_fields = ('user_id', 'email', 'institution')
    ordering = ('user_id',)