from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as filters
from .models import Application
from .serializers import (
    ApplicationSerializer,
    ApplicationCreateSerializer,
    ApplicationStatusUpdateSerializer,
    ApplicationExportSerializer
)
from users.permissions import IsOwnerOrAdmin
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

class ApplicationFilter(filters.FilterSet):
    status = filters.CharFilter(field_name='status')
    applied_after = filters.DateTimeFilter(field_name='applied_at', lookup_expr='gte')
    opportunity = filters.UUIDFilter(field_name='opportunity')
    
    class Meta:
        model = Application
        fields = ['status', 'opportunity']

class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    filterset_class = ApplicationFilter
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'administrator':
            return Application.objects.all()
        return Application.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return ApplicationCreateSerializer
        if self.action == 'update_status':
            return ApplicationStatusUpdateSerializer
        return ApplicationSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(
        tags=['Applications'],
        description='Update application status (admin only)',
        request=ApplicationStatusUpdateSerializer,
        responses={200: ApplicationSerializer}
    )
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        if request.user.role != 'administrator':
            return Response(
                {"error": "Only administrators can update application status"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        application = self.get_object()
        serializer = ApplicationStatusUpdateSerializer(
            application, data=request.data, partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        tags=['Applications'],
        description='Get application statistics',
        responses={
            200: {
                'description': 'Application statistics',
                'examples': [{
                    'total': 50,
                    'by_status': {
                        'pending': 20,
                        'under_review': 10,
                        'shortlisted': 8,
                        'accepted': 5,
                        'rejected': 5,
                        'withdrawn': 2
                    }
                }]
            }
        }
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        applications = self.get_queryset()
        stats = {
            'total': applications.count(),
            'by_status': {
                status: applications.filter(status=status).count()
                for status in ['pending', 'under_review', 'shortlisted', 
                             'accepted', 'rejected', 'withdrawn']
            }
        }
        return Response(stats)

    @action(detail=True, methods=['post'])
    def schedule_interview(self, request, pk=None):
        """Schedule or update interview for an application"""
        application = self.get_object()
        interview_date = request.data.get('interview_date')
        interview_notes = request.data.get('interview_notes', '')
        
        application.interview_date = interview_date
        application.admin_notes = interview_notes
        application.status = 'shortlisted'
        application.save()
        
        # Send email notification to student
        return Response({'message': 'Interview scheduled successfully'})

    @action(detail=True, methods=['post'])
    def submit_feedback(self, request, pk=None):
        """Submit interview feedback"""
        application = self.get_object()
        feedback = request.data.get('feedback')
        decision = request.data.get('decision')  # accept/reject
        
        application.interview_feedback = feedback
        application.status = decision
        application.save()
        
        # Send email notification to student
        return Response({'message': 'Feedback submitted successfully'})

    @action(detail=True, methods=['post'])
    def upload_resume(self, request, pk=None):
        """Upload or update resume for an application"""
        application = self.get_object()
        
        if 'resume' not in request.FILES:
            return Response(
                {"error": "No resume file provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        resume_file = request.FILES['resume']
        
        # Check file size (10MB limit)
        if resume_file.size > 10 * 1024 * 1024:
            return Response(
                {"error": "File size exceeds 10MB limit"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Check file type
        allowed_types = ['application/pdf', 'application/msword', 
                        'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
        if resume_file.content_type not in allowed_types:
            return Response(
                {"error": "Invalid file type. Only PDF and Word documents are allowed"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Delete old resume if it exists
        if application.resume:
            application.resume.delete()
            
        application.resume = resume_file
        application.save()
        
        return Response({
            'message': 'Resume uploaded successfully',
            'resume_url': application.resume.url
        })

    @action(detail=False, methods=['get'])
    def export_data(self, request):
        """Export applications data (admin only)"""
        if not request.user.role == 'administrator':
            return Response(
                {"error": "Only administrators can export data"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        applications = self.get_queryset()
        serializer = ApplicationExportSerializer(applications, many=True)
        
        # Format data for export
        return Response(serializer.data) 