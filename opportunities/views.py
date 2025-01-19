from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as filters
from .models import Opportunity
from applications.models import Application
from .serializers import OpportunitySerializer, OpportunityListSerializer
from users.permissions import IsOwnerOrAdmin
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.db.models import Count
from django.db.models.functions import TruncDate

class OpportunityFilter(filters.FilterSet):
    type = filters.CharFilter(field_name='type')
    status = filters.CharFilter(field_name='status')
    organization = filters.CharFilter(field_name='organization', lookup_expr='icontains')
    location = filters.CharFilter(field_name='location', lookup_expr='icontains')
    deadline_after = filters.DateTimeFilter(field_name='application_deadline', lookup_expr='gte')
    
    class Meta:
        model = Opportunity
        fields = ['type', 'status', 'organization', 'location']

class OpportunityViewSet(viewsets.ModelViewSet):
    queryset = Opportunity.objects.all()
    serializer_class = OpportunitySerializer
    filterset_class = OpportunityFilter
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Opportunity.objects.all()
        if self.request.user.role != 'administrator':
            queryset = queryset.filter(status='active')
        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return OpportunityListSerializer
        return OpportunitySerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @extend_schema(
        tags=['Opportunities'],
        description='List all opportunities',
        parameters=[
            OpenApiParameter('type', OpenApiTypes.STR, 
                enum=['internship', 'job', 'project', 'research']),
            OpenApiParameter('status', OpenApiTypes.STR, 
                enum=['draft', 'active', 'closed', 'archived']),
            OpenApiParameter('organization', OpenApiTypes.STR),
            OpenApiParameter('location', OpenApiTypes.STR),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        tags=['Opportunities'],
        description='Create new opportunity (admin only)'
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        tags=['Opportunities'],
        description='Toggle save status of an opportunity',
        responses={200: {'saved': True}}
    )
    @action(detail=True, methods=['post'])
    def toggle_save(self, request, pk=None):
        opportunity = self.get_object()
        user = request.user
        
        if opportunity.saved_by.filter(id=user.id).exists():
            opportunity.saved_by.remove(user)
            saved = False
        else:
            opportunity.saved_by.add(user)
            saved = True
            
        return Response({'saved': saved})

    @action(detail=False, methods=['get'])
    def saved(self, request):
        saved_opportunities = Opportunity.objects.filter(saved_by=request.user)
        serializer = OpportunityListSerializer(saved_opportunities, many=True)
        return Response(serializer.data)

    @extend_schema(
        tags=['Opportunities'],
        description='Get opportunity statistics (admin only)',
        responses={
            200: {
                'description': 'Opportunity statistics',
                'examples': [{
                    'total_opportunities': 50,
                    'active_opportunities': 30,
                    'total_applications': 150,
                    'average_applications': 3.0
                }]
            }
        }
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        if request.user.role != 'administrator':
            return Response(
                {"error": "Only administrators can access stats"},
                status=status.HTTP_403_FORBIDDEN
            )

        total = Opportunity.objects.count()
        active = Opportunity.objects.filter(status='active').count()
        applications = sum(o.applications_count for o in Opportunity.objects.all())
        
        return Response({
            'total_opportunities': total,
            'active_opportunities': active,
            'total_applications': applications,
            'average_applications': applications/total if total > 0 else 0
        })

    @action(detail=True, methods=['post'])
    def bulk_status_update(self, request, pk=None):
        """Update status of multiple applications for an opportunity"""
        opportunity = self.get_object()
        application_ids = request.data.get('application_ids', [])
        new_status = request.data.get('status')
        
        if not request.user.role == 'administrator':
            return Response(
                {"error": "Only administrators can perform bulk updates"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        Application.objects.filter(
            opportunity=opportunity,
            id__in=application_ids
        ).update(status=new_status)
        
        return Response({'message': 'Applications updated successfully'})

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Create a copy of an existing opportunity"""
        opportunity = self.get_object()
        opportunity.pk = None
        opportunity.title = f"Copy of {opportunity.title}"
        opportunity.status = 'draft'
        opportunity.save()
        return Response(OpportunitySerializer(opportunity).data)

    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get detailed analytics for opportunities"""
        if not request.user.role == 'administrator':
            return Response(
                {"error": "Only administrators can access analytics"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        return Response({
            'by_type': dict(
                Opportunity.objects.values_list('type')
                .annotate(count=Count('id'))
            ),
            'by_status': dict(
                Opportunity.objects.values_list('status')
                .annotate(count=Count('id'))
            ),
            'application_trends': dict(
                Application.objects.annotate(
                    date=TruncDate('applied_at')
                )
                .values('date')
                .annotate(count=Count('id'))
                .order_by('-date')[:30]
            )
        })

    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Get total stats for the dashboard including total counts without pagination"""
        user = request.user
        
        # Get all opportunities
        all_opportunities = self.get_queryset()
        total_count = all_opportunities.count()
        active_count = all_opportunities.filter(status='active').count()
        
        # Get user's saved opportunities
        saved_count = Opportunity.objects.filter(saved_by=user).count()
        
        # Get user's applications
        user_applications = Application.objects.filter(user=user)
        total_applications = user_applications.count()
        accepted_applications = user_applications.filter(status='accepted').count()
        
        # Calculate success rate
        success_rate = (accepted_applications / total_applications * 100) if total_applications > 0 else 0
        
        return Response({
            'total_opportunities': total_count,
            'active_opportunities': active_count,
            'saved_opportunities': saved_count,
            'pending_applications': total_applications,
            'accepted_applications': accepted_applications,
            'success_rate': round(success_rate)
        }) 