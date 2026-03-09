from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('auth/signup/', views.signup, name='signup'),
    path('auth/login/', views.login, name='login'),
    
    # Categories
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    
    # Notes CRUD
    path('notes/', views.NoteListView.as_view(), name='note-list'),
    path('notes/create/', views.NoteCreateView.as_view(), name='note-create'),
    path('notes/<int:pk>/', views.NoteRetrieveView.as_view(), name='note-detail'),
    path('notes/<int:pk>/update/', views.NoteUpdateView.as_view(), name='note-update'),
    path('notes/<int:pk>/delete/', views.NoteDeleteView.as_view(), name='note-delete'),
]