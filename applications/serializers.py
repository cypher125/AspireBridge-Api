from rest_framework import serializers
from .models import Application
from users.serializers import UserSerializer
from opportunities.models import Opportunity

class OpportunityBasicSerializer(serializers.ModelSerializer):
    """Basic Opportunity serializer to avoid circular imports"""
    class Meta:
        model = Opportunity
        fields = ['id', 'title', 'organization', 'type', 'location']

class ApplicationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    opportunity = OpportunityBasicSerializer(read_only=True)
    
    class Meta:
        model = Application
        fields = '__all__'
        read_only_fields = ('user', 'applied_at', 'updated_at')

class ApplicationCreateSerializer(serializers.ModelSerializer):
    resume = serializers.FileField(required=True)
    
    class Meta:
        model = Application
        fields = ['opportunity', 'cover_letter', 'resume']
        
    def validate_resume(self, value):
        if value:
            # Check file size (max 5MB)
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError("File size too large. Maximum size is 5MB.")
            
            # Check file type
            allowed_types = ['application/pdf', 'application/msword', 
                           'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
            if value.content_type not in allowed_types:
                raise serializers.ValidationError("Invalid file type. Please upload a PDF or Word document.")
        return value

class ApplicationListSerializer(serializers.ModelSerializer):
    opportunity = OpportunityBasicSerializer(read_only=True)
    
    class Meta:
        model = Application
        fields = ['id', 'opportunity', 'status', 'applied_at', 'interview_date']

class ApplicationStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['status', 'admin_notes', 'interview_date', 'interview_feedback', 'rejection_reason']

class ApplicationExportSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email')
    user_name = serializers.CharField(source='user.name')
    opportunity_title = serializers.CharField(source='opportunity.title')
    organization = serializers.CharField(source='opportunity.organization')
    
    class Meta:
        model = Application
        fields = [
            'id',
            'user_email',
            'user_name',
            'opportunity_title',
            'organization',
            'status',
            'applied_at',
            'interview_date',
            'cover_letter',
            'admin_notes',
            'interview_feedback',
            'rejection_reason'
        ] 