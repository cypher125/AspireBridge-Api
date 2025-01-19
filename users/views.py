from rest_framework import viewsets, status, generics
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from .serializers import (
    UserSerializer, 
    MultiStepRegistrationSerializer,
    CustomTokenObtainPairSerializer,
    UserStatsSerializer
)
from .permissions import IsOwnerOrAdmin
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from django.contrib.auth.tokens import default_token_generator
from opportunities.models import Opportunity
from applications.models import Application

User = get_user_model()

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    @extend_schema(
        tags=['Authentication'],
        description='Login endpoint to obtain JWT tokens',
        responses={
            200: {
                'description': 'Successfully authenticated',
                'examples': [{
                    'access': 'string',
                    'refresh': 'string',
                    'user': {
                        'id': 'uuid',
                        'email': 'user@example.com',
                        'name': 'John Doe',
                        'role': 'student'
                    }
                }]
            }
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class RegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = MultiStepRegistrationSerializer

    @extend_schema(
        tags=['Authentication'],
        description='''
        Multi-step registration endpoint.
        
        Steps:
        1. Basic Information (email, password, name)
        2. Role Selection (student/administrator)
        3. Additional Details (based on role)
        ''',
        request=MultiStepRegistrationSerializer,
        responses={201: UserSerializer}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        if self.request.user.role == 'administrator':
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

    @extend_schema(
        tags=['Users'],
        description='Get list of users (admin only)',
        parameters=[
            OpenApiParameter('role', OpenApiTypes.STR, enum=['student', 'administrator']),
            OpenApiParameter('search', OpenApiTypes.STR, description='Search by name or email'),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        tags=['Users'],
        description='Get current user profile'
    )
    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @extend_schema(
        tags=['Users'],
        description='Get user statistics (admin only)',
        responses={
            200: {
                'description': 'User statistics',
                'examples': [{
                    'total_users': 100,
                    'active_users': 80,
                    'new_users_this_month': 20,
                    'user_roles': {
                        'student': 90,
                        'administrator': 10
                    }
                }]
            }
        }
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        if not request.user.role == 'administrator':
            return Response(
                {"error": "Only administrators can access stats"},
                status=status.HTTP_403_FORBIDDEN
            )

        now = timezone.now()
        month_ago = now - timedelta(days=30)

        stats = {
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'new_users_this_month': User.objects.filter(join_date__gte=month_ago).count(),
            'user_roles': dict(User.objects.values_list('role').annotate(count=Count('id')))
        }

        serializer = UserStatsSerializer(stats)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def update_profile_picture(self, request, pk=None):
        user = self.get_object()
        if 'profile_picture' not in request.FILES:
            return Response(
                {'error': 'No image provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.profile_picture = request.FILES['profile_picture']
        user.save()
        user.calculate_completion_rate()
        return Response(UserSerializer(user).data)

    def perform_update(self, serializer):
        instance = serializer.save()
        instance.calculate_completion_rate() 

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Allow users to change their password"""
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not user.check_password(old_password):
            return Response(
                {'error': 'Invalid old password'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        user.set_password(new_password)
        user.save()
        return Response({'message': 'Password updated successfully'})

    @action(detail=False, methods=['post'])
    def forgot_password(self, request):
        """Initiate password reset process"""
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            # Generate reset token and send email
            token = default_token_generator.make_token(user)
            # Send password reset email
            return Response({'message': 'Password reset email sent'})
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Get user-specific dashboard statistics"""
        user = request.user
        if user.role == 'student':
            stats = {
                'applications_count': user.applications.count(),
                'pending_applications': user.applications.filter(status='pending').count(),
                'accepted_applications': user.applications.filter(status='accepted').count(),
                'saved_opportunities': user.saved_opportunities.count(),
                'upcoming_interviews': user.applications.filter(
                    interview_date__gte=timezone.now()
                ).count()
            }
        else:  # administrator
            stats = {
                'total_opportunities': Opportunity.objects.filter(created_by=user).count(),
                'active_opportunities': Opportunity.objects.filter(
                    created_by=user, 
                    status='active'
                ).count(),
                'total_applications_received': Application.objects.filter(
                    opportunity__created_by=user
                ).count(),
                'pending_reviews': Application.objects.filter(
                    opportunity__created_by=user,
                    status='pending'
                ).count()
            }
        return Response(stats) 