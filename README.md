# Notes Backend API

Django REST Framework backend for the Notes application.

## Process

My process consisted on:
1. Understand the project requirements from the figma files and outline the scope of the app.
2. I started with the backend app by modeling the database, working on the endpoints and setting the test suite.
3. Then, I started with the frontend without applying styles yet but creating the main functionality of the app and integrating with the backend.
4. Once the frontend was working properly along the backend, I started styling the app according to the figma file and taking care of the minor details.
5. Finally, I dockerized both frontend and backend to be production-ready.

## Technical decisions

Main technical decisions I made were:
- Two separate repos for backend and frontend with latest versions of python and nextjs.
- Used postgres as database.
- Used docker for both frontend and backend.
- Implemented auto save on frontend to work like Apple Notes so user doesn't need to click on save.
- Make the frontend responsive so it's also visible in mobile devices.

## AI Tools used

Used Claude Code for both repos. Most of the code in backend is AI-generated while in frontend I need to make a lot of speficic style adjustments that were easier to apply in the code editor.
Also used AI to generate the tests so I can ensure backend won't break with new features. With Claude Code I was able to complete both repos in about 8 hours.

## Setup

### Local Development
```bash
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Docker Setup
```bash
# Run with PostgreSQL database
docker-compose up

# Production (without database)
docker-compose -f docker-compose-prod.yml up

# Database credentials (development):
# - Host: localhost:5432
# - Database: notes_db
# - Username: postgres
# - Password: postgres
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
**42 tests total** covering complete API functionality:

#### Authentication Tests (14 tests) - `tests/test_auth.py`
- **Signup Endpoint (7 tests)**:
  - Successful registration with JWT tokens
  - Email normalization (lowercase, trimmed)
  - Duplicate email prevention (case insensitive)
  - Required field validation
  - Invalid email format handling
- **Login Endpoint (7 tests)**:
  - Successful authentication
  - Email normalization
  - Invalid credentials handling
  - Inactive user prevention
  - Required field validation

#### Notes & Categories Tests (28 tests) - `tests/test_notes.py`
- **Categories Endpoint (3 tests)**:
  - Authenticated listing with note counts
  - Authentication required
- **Notes CRUD (25 tests)**:
  - **List** (7 tests): Pagination, user isolation, soft delete filtering
  - **Create** (4 tests): Authentication, validation, category assignment
  - **Retrieve** (5 tests): Owner access, authentication, 404 handling
  - **Update** (5 tests): Full/partial updates, ownership validation
  - **Delete** (4 tests): Soft delete, ownership, already deleted handling

### Test Features
- Database isolation with `@pytest.mark.django_db`
- Factory-based test data generation (Factory Boy)
- JWT authentication flow testing
- User isolation and ownership validation
- Soft delete functionality verification
- Pagination and filtering validation
- Comprehensive error handling coverage

## Configuration
- PostgreSQL database
- CORS enabled for frontend
- Email-based authentication
- API schema documentation with drf-spectacular
