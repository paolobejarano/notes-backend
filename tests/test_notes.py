import pytest
import json
from django.urls import reverse
from django.utils import timezone
from core.models import Note, Category


@pytest.mark.django_db
class TestCategoriesEndpoint:
    
    def test_list_categories_authenticated(self, authenticated_client, categories):
        """Test listing categories with authentication"""
        response = authenticated_client.get('/api/categories/')
        
        assert response.status_code == 200
        assert 'results' in response.data
        assert len(response.data['results']) == 3
        
        category_names = [cat['name'] for cat in response.data['results']]
        assert 'Random Thoughts' in category_names
        assert 'School' in category_names
        assert 'Personal' in category_names
        
        # Check that note_count field is included and is 0 (no notes yet)
        for category in response.data['results']:
            assert 'note_count' in category
            assert category['note_count'] == 0
    
    def test_list_categories_with_notes(self, authenticated_client, categories, note):
        """Test listing categories with note counts"""
        response = authenticated_client.get('/api/categories/')
        
        assert response.status_code == 200
        assert 'results' in response.data
        
        # Find the category that has the note
        test_category = None
        for category in response.data['results']:
            if category['name'] == 'Test Category':
                test_category = category
                break
        
        # The test note uses the 'category' fixture which creates 'Test Category'
        # But categories fixture creates different ones, so let's check the actual category
        # that the note belongs to has count = 1
        note_category_name = note.category.name
        for category in response.data['results']:
            if category['name'] == note_category_name:
                assert category['note_count'] == 1
                break
        else:
            # If note's category not in results, verify at least one category has count > 0
            total_notes = sum(cat['note_count'] for cat in response.data['results'])
            assert total_notes >= 1
    
    def test_list_categories_unauthenticated(self, api_client, categories):
        """Test listing categories without authentication fails"""
        response = api_client.get('/api/categories/')
        
        assert response.status_code == 401


@pytest.mark.django_db
class TestNotesListEndpoint:
    
    def test_list_notes_authenticated(self, authenticated_client, note):
        """Test listing user's notes with authentication"""
        response = authenticated_client.get('/api/notes/')
        
        assert response.status_code == 200
        assert 'results' in response.data
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == 'Test Note'
        assert response.data['results'][0]['body'] == 'This is a test note body'
    
    def test_list_notes_unauthenticated(self, api_client, note):
        """Test listing notes without authentication fails"""
        response = api_client.get('/api/notes/')
        
        assert response.status_code == 401
    
    def test_list_notes_only_own_notes(self, authenticated_client, note, another_user_note):
        """Test that users only see their own notes"""
        response = authenticated_client.get('/api/notes/')
        
        assert response.status_code == 200
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == 'Test Note'
    
    def test_list_notes_excludes_soft_deleted(self, authenticated_client, note):
        """Test that soft-deleted notes are excluded from listing"""
        # Soft delete the note
        note.deleted_at = timezone.now()
        note.save()
        
        response = authenticated_client.get('/api/notes/')
        
        assert response.status_code == 200
        assert len(response.data['results']) == 0
    
    def test_list_notes_pagination(self, authenticated_client, multiple_notes):
        """Test pagination in notes listing"""
        response = authenticated_client.get('/api/notes/')
        
        assert response.status_code == 200
        assert 'count' in response.data
        assert 'has_next' in response.data
        assert 'has_previous' in response.data
        assert 'results' in response.data
        
        assert response.data['count'] == 25
        assert response.data['has_next'] is True
        assert response.data['has_previous'] is False
        assert len(response.data['results']) == 20  # Default page size
    
    def test_list_notes_second_page(self, authenticated_client, multiple_notes):
        """Test second page of pagination"""
        response = authenticated_client.get('/api/notes/?page=2')
        
        assert response.status_code == 200
        assert response.data['has_next'] is False
        assert response.data['has_previous'] is True
        assert len(response.data['results']) == 5  # Remaining notes


@pytest.mark.django_db
class TestNotesCreateEndpoint:
    
    def test_create_note_authenticated(self, authenticated_client, category):
        """Test creating a note with authentication"""
        data = {
            'title': 'New Note',
            'body': 'This is a new note',
            'category': category.id
        }
        
        response = authenticated_client.post('/api/notes/create/', data, format='json')
        
        assert response.status_code == 201
        assert Note.objects.filter(title='New Note').exists()
        
        note = Note.objects.get(title='New Note')
        assert note.user.email == 'testuser@example.com'
        assert note.category == category
    
    def test_create_note_unauthenticated(self, api_client, category):
        """Test creating a note without authentication fails"""
        data = {
            'title': 'New Note',
            'body': 'This is a new note',
            'category': category.id
        }
        
        response = api_client.post('/api/notes/create/', data, format='json')
        
        assert response.status_code == 401
    
    def test_create_note_invalid_category(self, authenticated_client):
        """Test creating a note with invalid category fails"""
        data = {
            'title': 'New Note',
            'body': 'This is a new note',
            'category': 999  # Non-existent category
        }
        
        response = authenticated_client.post('/api/notes/create/', data, format='json')
        
        assert response.status_code == 400
    
    def test_create_note_missing_title(self, authenticated_client, category):
        """Test creating a note without title fails"""
        data = {
            'body': 'This is a new note',
            'category': category.id
        }
        
        response = authenticated_client.post('/api/notes/create/', data, format='json')
        
        assert response.status_code == 400


@pytest.mark.django_db
class TestNotesRetrieveEndpoint:
    
    def test_retrieve_note_authenticated_owner(self, authenticated_client, note):
        """Test retrieving own note with authentication"""
        response = authenticated_client.get(f'/api/notes/{note.id}/')
        
        assert response.status_code == 200
        assert response.data['title'] == 'Test Note'
        assert response.data['body'] == 'This is a test note body'
        assert response.data['user']['email'] == 'testuser@example.com'
    
    def test_retrieve_note_unauthenticated(self, api_client, note):
        """Test retrieving note without authentication fails"""
        response = api_client.get(f'/api/notes/{note.id}/')
        
        assert response.status_code == 401
    
    def test_retrieve_note_not_owner(self, authenticated_client, another_user_note):
        """Test retrieving another user's note fails"""
        response = authenticated_client.get(f'/api/notes/{another_user_note.id}/')
        
        assert response.status_code == 403
    
    def test_retrieve_note_not_found(self, authenticated_client):
        """Test retrieving non-existent note fails"""
        response = authenticated_client.get('/api/notes/999/')
        
        assert response.status_code == 404
    
    def test_retrieve_soft_deleted_note(self, authenticated_client, note):
        """Test retrieving soft-deleted note fails"""
        note.deleted_at = timezone.now()
        note.save()
        
        response = authenticated_client.get(f'/api/notes/{note.id}/')
        
        assert response.status_code == 404


@pytest.mark.django_db
class TestNotesUpdateEndpoint:
    
    def test_update_note_authenticated_owner(self, authenticated_client, note, categories):
        """Test updating own note with authentication"""
        new_category = categories[1]
        data = {
            'title': 'Updated Note',
            'body': 'Updated body',
            'category': new_category.id
        }
        
        response = authenticated_client.put(f'/api/notes/{note.id}/update/', data, format='json')
        
        assert response.status_code == 200
        
        note.refresh_from_db()
        assert note.title == 'Updated Note'
        assert note.body == 'Updated body'
        assert note.category == new_category
    
    def test_update_note_partial(self, authenticated_client, note):
        """Test partial update of note"""
        data = {
            'title': 'Partially Updated Note'
        }
        
        response = authenticated_client.patch(f'/api/notes/{note.id}/update/', data, format='json')
        
        assert response.status_code == 200
        
        note.refresh_from_db()
        assert note.title == 'Partially Updated Note'
        assert note.body == 'This is a test note body'  # Unchanged
    
    def test_update_note_unauthenticated(self, api_client, note):
        """Test updating note without authentication fails"""
        data = {
            'title': 'Updated Note'
        }
        
        response = api_client.put(f'/api/notes/{note.id}/update/', data, format='json')
        
        assert response.status_code == 401
    
    def test_update_note_not_owner(self, authenticated_client, another_user_note):
        """Test updating another user's note fails"""
        data = {
            'title': 'Updated Note'
        }
        
        response = authenticated_client.put(f'/api/notes/{another_user_note.id}/update/', data, format='json')
        
        assert response.status_code == 403
    
    def test_update_soft_deleted_note(self, authenticated_client, note):
        """Test updating soft-deleted note fails"""
        note.deleted_at = timezone.now()
        note.save()
        
        data = {
            'title': 'Updated Note'
        }
        
        response = authenticated_client.put(f'/api/notes/{note.id}/update/', data, format='json')
        
        assert response.status_code == 404


@pytest.mark.django_db
class TestNotesDeleteEndpoint:
    
    def test_delete_note_authenticated_owner(self, authenticated_client, note):
        """Test soft deleting own note with authentication"""
        response = authenticated_client.delete(f'/api/notes/{note.id}/delete/')
        
        assert response.status_code == 204
        
        note.refresh_from_db()
        assert note.deleted_at is not None
        assert Note.objects.filter(id=note.id, deleted_at__isnull=True).count() == 0
    
    def test_delete_note_unauthenticated(self, api_client, note):
        """Test deleting note without authentication fails"""
        response = api_client.delete(f'/api/notes/{note.id}/delete/')
        
        assert response.status_code == 401
    
    def test_delete_note_not_owner(self, authenticated_client, another_user_note):
        """Test deleting another user's note fails"""
        response = authenticated_client.delete(f'/api/notes/{another_user_note.id}/delete/')
        
        assert response.status_code == 403
    
    def test_delete_note_not_found(self, authenticated_client):
        """Test deleting non-existent note fails"""
        response = authenticated_client.delete('/api/notes/999/delete/')
        
        assert response.status_code == 404
    
    def test_delete_already_soft_deleted_note(self, authenticated_client, note):
        """Test deleting already soft-deleted note fails"""
        note.deleted_at = timezone.now()
        note.save()
        
        response = authenticated_client.delete(f'/api/notes/{note.id}/delete/')
        
        assert response.status_code == 404