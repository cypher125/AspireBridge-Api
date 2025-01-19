from django.contrib import admin
from .models import Opportunity

@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ('title', 'organization', 'type', 'status', 'created_by', 
                   'application_deadline', 'applications_count')
    list_filter = ('status', 'type', 'organization')
    search_fields = ('title', 'description', 'organization')
    readonly_fields = ('created_at', 'updated_at', 'views_count', 'applications_count')
    date_hierarchy = 'created_at'
