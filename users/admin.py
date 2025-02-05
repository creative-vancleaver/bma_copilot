from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):

    list_display = ('email', 'institution', 'is_staff')
    search_fields = ('email', 'institution')
    ordering = ('email',)