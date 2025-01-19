from rest_framework import serializers
from .models import Opportunity

class OpportunityListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Opportunity
        fields = ['id', 'title', 'organization', 'type', 'location', 
                 'status', 'application_deadline', 'applications_count']

class OpportunitySerializer(serializers.ModelSerializer):
    is_saved = serializers.SerializerMethodField()
    has_applied = serializers.SerializerMethodField()
    
    class Meta:
        model = Opportunity
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by',
                           'views_count', 'applications_count', 'is_saved', 'has_applied']

    def get_is_saved(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.saved_by.filter(id=request.user.id).exists()
        return False

    def get_has_applied(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.applications.filter(user=request.user).exists()
        return False 