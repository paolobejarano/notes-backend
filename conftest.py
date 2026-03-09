import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from core.models import Category, Note


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_data():
    return {
        'email': 'testuser@example.com',
        'password': 'testpassword123'
    }


@pytest.fixture
def existing_user(db, user_data):
    return User.objects.create_user(
        username=user_data['email'],
        email=user_data['email'],
        password=user_data['password']
    )


@pytest.fixture
def another_user(db):
    return User.objects.create_user(
        username='another@example.com',
        email='another@example.com',
        password='anotherpass123'
    )


@pytest.fixture
def authenticated_client(api_client, existing_user):
    refresh = RefreshToken.for_user(existing_user)
    access_token = refresh.access_token
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    return api_client


@pytest.fixture
def category(db):
    return Category.objects.create(
        name='Test Category',
        color='#FF5733'
    )


@pytest.fixture
def categories(db):
    categories_data = [
        {'name': 'Random Thoughts', 'color': '#EF9C66'},
        {'name': 'School', 'color': '#FCDC94'},
        {'name': 'Personal', 'color': '#78ABA8'},
    ]
    
    categories = []
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={'color': cat_data['color']}
        )
        categories.append(category)
    
    return categories


@pytest.fixture
def note(db, existing_user, category):
    return Note.objects.create(
        title='Test Note',
        body='This is a test note body',
        user=existing_user,
        category=category
    )


@pytest.fixture
def multiple_notes(db, existing_user, category):
    notes = []
    for i in range(25):  # Create 25 notes for pagination testing
        notes.append(Note.objects.create(
            title=f'Note {i+1}',
            body=f'This is test note {i+1} body',
            user=existing_user,
            category=category
        ))
    return notes


@pytest.fixture
def another_user_note(db, another_user, category):
    return Note.objects.create(
        title='Another User Note',
        body='This note belongs to another user',
        user=another_user,
        category=category
    )
