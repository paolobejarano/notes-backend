from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema
from django.utils import timezone
from .models import Note, Category
from .pagination import NotesPagination
from .serializers import (
    SignupSerializer, LoginSerializer, AuthResponseSerializer,
    NoteSerializer, NoteCreateSerializer, NoteUpdateSerializer, CategorySerializer
)


@extend_schema(
    request=SignupSerializer,
    responses={
        201: AuthResponseSerializer,
        400: 'Bad Request'
    },
    summary="User Signup",
    description="Register a new user account with email and password. Returns JWT tokens for authentication."
)
@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = SignupSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        return Response({
            'message': 'User created successfully',
            'user': {
                'id': user.id,
                'email': user.email
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(access_token)
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    request=LoginSerializer,
    responses={
        200: AuthResponseSerializer,
        400: 'Bad Request'
    },
    summary="User Login",
    description="Authenticate user with email and password. Returns JWT tokens for subsequent API requests."
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        return Response({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'email': user.email
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(access_token)
            }
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Categories endpoint
@extend_schema(
    responses={200: CategorySerializer(many=True)},
    summary="List Categories",
    description="Get all available note categories."
)
class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


# Notes CRUD endpoints
@extend_schema(
    responses={200: NoteSerializer(many=True)},
    summary="List User Notes",
    description="Get all notes for the authenticated user (excluding soft-deleted notes)."
)
class NoteListView(generics.ListAPIView):
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = NotesPagination
    
    def get_queryset(self):
        queryset = Note.objects.filter(
            user=self.request.user,
            deleted_at__isnull=True
        ).select_related('category', 'user').order_by('-updated_at')
        
        # Filter by category if provided
        category_id = self.request.query_params.get('category', None)
        if category_id:
            try:
                category_id = int(category_id)
                queryset = queryset.filter(category_id=category_id)
            except (ValueError, TypeError):
                # Invalid category ID, ignore filter
                pass
        
        return queryset


@extend_schema(
    request=NoteCreateSerializer,
    responses={201: NoteSerializer, 400: 'Bad Request'},
    summary="Create Note",
    description="Create a new note for the authenticated user."
)
class NoteCreateView(generics.CreateAPIView):
    serializer_class = NoteCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@extend_schema(
    responses={200: NoteSerializer, 404: 'Not Found'},
    summary="Get Note",
    description="Get a specific note by ID. User must own the note."
)
class NoteRetrieveView(generics.RetrieveAPIView):
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        try:
            note = Note.objects.select_related('category', 'user').get(
                id=self.kwargs['pk'],
                deleted_at__isnull=True
            )
        except Note.DoesNotExist:
            raise NotFound("Note not found")
        
        # Check ownership
        if note.user != self.request.user:
            raise PermissionDenied("You don't have permission to access this note")
        
        return note


@extend_schema(
    request=NoteUpdateSerializer,
    responses={200: NoteSerializer, 400: 'Bad Request', 404: 'Not Found', 403: 'Forbidden'},
    summary="Update Note",
    description="Update a note. User must own the note."
)
class NoteUpdateView(generics.UpdateAPIView):
    serializer_class = NoteUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        try:
            note = Note.objects.get(
                id=self.kwargs['pk'],
                deleted_at__isnull=True
            )
        except Note.DoesNotExist:
            raise NotFound("Note not found")
        
        # Check ownership
        if note.user != self.request.user:
            raise PermissionDenied("You don't have permission to edit this note")
        
        return note


@extend_schema(
    responses={204: None, 404: 'Not Found', 403: 'Forbidden'},
    summary="Delete Note",
    description="Soft delete a note. User must own the note."
)
class NoteDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        try:
            note = Note.objects.get(
                id=self.kwargs['pk'],
                deleted_at__isnull=True
            )
        except Note.DoesNotExist:
            raise NotFound("Note not found")
        
        # Check ownership
        if note.user != self.request.user:
            raise PermissionDenied("You don't have permission to delete this note")
        
        return note
    
    def perform_destroy(self, instance):
        # Soft delete: set deleted_at timestamp instead of actually deleting
        instance.deleted_at = timezone.now()
        instance.save()
