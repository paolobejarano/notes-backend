# Notes Backend API

Django REST Framework backend for the Notes application.

## Setup
```bash
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## API Endpoints

### Authentication
- `POST /api/auth/signup/` - User registration (email, password)
- `POST /api/auth/login/` - User login (email, password)

### Categories
- `GET /api/categories/` - List categories with note counts

### Notes CRUD
- `GET /api/notes/` - List user notes (paginated, filterable by `?category=id`)
- `POST /api/notes/create/` - Create note
- `GET /api/notes/{id}/` - Get specific note
- `PUT/PATCH /api/notes/{id}/update/` - Update note
- `DELETE /api/notes/{id}/delete/` - Soft delete note

### Documentation
- `GET /docs/` - Interactive Swagger UI

## Models

### Category
- `name` (unique)
- `color` (hex)
- `created_at`

### Note  
- `title`
- `body` (nullable)
- `user` (ForeignKey)
- `category` (ForeignKey)
- `deleted_at` (nullable, for soft delete)
- `created_at`, `updated_at`

## Features
- JWT authentication (7-day tokens)
- User isolation & ownership validation
- Soft delete functionality
- Email standardization (lowercase, trimmed)
- Pagination (20 items default, configurable)
- Comprehensive test suite (42 tests)

## Testing

### Setup
Tests use pytest with Django integration and database mocking.

```bash
# Install test dependencies (already included)
pip install pytest pytest-django pytest-cov factory-boy faker

# Run all tests
pytest

# Run with coverage
pytest --cov=core

# Run specific test file
pytest tests/test_auth.py
pytest tests/test_notes.py
```

### Test Coverage
- **42 tests total** - All authentication and CRUD functionality
- **Authentication tests** (14) - Signup, login, validation, edge cases
- **Notes & Categories tests** (28) - CRUD, pagination, filtering, ownership

### Test Features
- Database mocking with `@pytest.mark.django_db`
- JWT token generation and authentication testing
- User isolation and ownership validation
- Soft delete functionality verification
- Pagination and filtering tests

## Configuration
- PostgreSQL database
- CORS enabled for frontend
- Email-based authentication
- API schema documentation with drf-spectacular
