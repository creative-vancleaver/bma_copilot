from django.contrib import admin

from .models import Case

@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):

    list_display = ('name', 'date', 'status')
    search_fields = ('name', 'description')
