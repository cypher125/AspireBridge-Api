from django.contrib import admin
from .models import Application

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'opportunity', 'status', 'applied_at', 'interview_date')
    list_filter = ('status', 'applied_at', 'interview_date')
    search_fields = ('user__email', 'opportunity__title')
    readonly_fields = ('applied_at', 'updated_at')
    date_hierarchy = 'applied_at'
