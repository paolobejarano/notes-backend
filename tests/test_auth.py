import pytest
import json
from django.contrib.auth.models import User
from django.urls import reverse


@pytest.mark.django_db
class TestSignupEndpoint:
    
    def test_successful_signup(self, api_client):
        """Test successful user registration"""
        data = {
            'email': 'newuser@example.com',
            'password': 'testpass123'
        }
        
        response = api_client.post('/api/auth/signup/', data, format='json')
        
        assert response.status_code == 201
        assert response.data['message'] == 'User created successfully'
        assert 'user' in response.data
        assert 'tokens' in response.data
        assert response.data['user']['email'] == 'newuser@example.com'
        assert 'access' in response.data['tokens']
        assert 'refresh' in response.data['tokens']
        
        # Verify user was created in database
        assert User.objects.filter(email='newuser@example.com').exists()
    
    def test_signup_email_normalization(self, api_client):
        """Test that email is normalized (lowercase, stripped)"""
        data = {
            'email': '  UPPERCASE@EXAMPLE.COM  ',
            'password': 'testpass123'
        }
        
        response = api_client.post('/api/auth/signup/', data, format='json')
        
        assert response.status_code == 201
        assert response.data['user']['email'] == 'uppercase@example.com'
        
        # Verify normalized email in database
        user = User.objects.get(email='uppercase@example.com')
        assert user.email == 'uppercase@example.com'
    
    def test_signup_duplicate_email(self, api_client, existing_user):
        """Test signup with already registered email fails"""
        data = {
            'email': 'testuser@example.com',  # Same as existing_user
            'password': 'newpassword123'
        }
        
        response = api_client.post('/api/auth/signup/', data, format='json')
        
        assert response.status_code == 400
        assert 'email' in response.data
        assert 'already exists' in response.data['email'][0]
    
    def test_signup_duplicate_email_case_insensitive(self, api_client, existing_user):
        """Test signup fails with same email in different case"""
        data = {
            'email': 'TESTUSER@EXAMPLE.COM',  # Same as existing_user but uppercase
            'password': 'newpassword123'
        }
        
        response = api_client.post('/api/auth/signup/', data, format='json')
        
        assert response.status_code == 400
        assert 'email' in response.data
    
    def test_signup_missing_email(self, api_client):
        """Test signup fails without email"""
        data = {
            'password': 'testpass123'
        }
        
        response = api_client.post('/api/auth/signup/', data, format='json')
        
        assert response.status_code == 400
        assert 'email' in response.data
    
    def test_signup_missing_password(self, api_client):
        """Test signup fails without password"""
        data = {
            'email': 'test@example.com'
        }
        
        response = api_client.post('/api/auth/signup/', data, format='json')
        
        assert response.status_code == 400
        assert 'password' in response.data
    
    def test_signup_invalid_email(self, api_client):
        """Test signup fails with invalid email format"""
        data = {
            'email': 'invalid-email',
            'password': 'testpass123'
        }
        
        response = api_client.post('/api/auth/signup/', data, format='json')
        
        assert response.status_code == 400
        assert 'email' in response.data


@pytest.mark.django_db
class TestLoginEndpoint:
    
    def test_successful_login(self, api_client, existing_user):
        """Test successful user login"""
        data = {
            'email': 'testuser@example.com',
            'password': 'testpassword123'
        }
        
        response = api_client.post('/api/auth/login/', data, format='json')
        
        assert response.status_code == 200
        assert response.data['message'] == 'Login successful'
        assert 'user' in response.data
        assert 'tokens' in response.data
        assert response.data['user']['email'] == 'testuser@example.com'
        assert 'access' in response.data['tokens']
        assert 'refresh' in response.data['tokens']
    
    def test_login_email_normalization(self, api_client, existing_user):
        """Test login works with different email casing/spacing"""
        data = {
            'email': '  TESTUSER@EXAMPLE.COM  ',
            'password': 'testpassword123'
        }
        
        response = api_client.post('/api/auth/login/', data, format='json')
        
        assert response.status_code == 200
        assert response.data['user']['email'] == 'testuser@example.com'
    
    def test_login_invalid_email(self, api_client):
        """Test login fails with non-existent email"""
        data = {
            'email': 'nonexistent@example.com',
            'password': 'testpass123'
        }
        
        response = api_client.post('/api/auth/login/', data, format='json')
        
        assert response.status_code == 400
        assert 'non_field_errors' in response.data
        assert 'Invalid email or password' in response.data['non_field_errors'][0]
    
    def test_login_invalid_password(self, api_client, existing_user):
        """Test login fails with wrong password"""
        data = {
            'email': 'testuser@example.com',
            'password': 'wrongpassword'
        }
        
        response = api_client.post('/api/auth/login/', data, format='json')
        
        assert response.status_code == 400
        assert 'non_field_errors' in response.data
        assert 'Invalid email or password' in response.data['non_field_errors'][0]
    
    def test_login_missing_email(self, api_client):
        """Test login fails without email"""
        data = {
            'password': 'testpass123'
        }
        
        response = api_client.post('/api/auth/login/', data, format='json')
        
        assert response.status_code == 400
        assert 'email' in response.data
    
    def test_login_missing_password(self, api_client):
        """Test login fails without password"""
        data = {
            'email': 'test@example.com'
        }
        
        response = api_client.post('/api/auth/login/', data, format='json')
        
        assert response.status_code == 400
        assert 'password' in response.data
    
    def test_login_inactive_user(self, api_client, existing_user):
        """Test login fails for inactive user"""
        existing_user.is_active = False
        existing_user.save()
        
        data = {
            'email': 'testuser@example.com',
            'password': 'testpassword123'
        }
        
        response = api_client.post('/api/auth/login/', data, format='json')
        
        assert response.status_code == 400
        assert 'non_field_errors' in response.data
        assert 'User account is disabled' in response.data['non_field_errors'][0]