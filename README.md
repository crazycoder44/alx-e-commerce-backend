# E-Commerce Backend API

A robust Django REST Framework-based backend system for e-commerce applications featuring product catalog management, user authentication, and comprehensive API documentation.

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![Django Version](https://img.shields.io/badge/django-4.2.7-green.svg)](https://djangoproject.com)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Documentation](#documentation)
- [Quick Start](#quick-start)
- [API Endpoints](#api-endpoints)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## Features

- 🔐 **JWT Authentication** - Secure user registration, login, and token management
- 📦 **Product Management** - Full CRUD operations for products and categories
- 🔍 **Advanced Filtering** - Filter by category, price range, stock availability
- 📊 **Sorting & Pagination** - Efficient data retrieval with customizable sorting
- 📚 **API Documentation** - Interactive Swagger UI and ReDoc
- ⚡ **Performance Optimized** - Database indexing and query optimization
- 🔒 **Permission-based Access** - Owner and admin-level permissions
- 🎯 **RESTful Design** - Clean and intuitive API structure

## Tech Stack

- **Framework**: Django 4.2.7
- **API**: Django REST Framework 3.14.0
- **Database**: PostgreSQL
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Documentation**: drf-yasg (Swagger/OpenAPI)
- **Filtering**: django-filter
- **Image Processing**: Pillow

## 📚 Documentation

- **[API Guide](API_GUIDE.md)** - Comprehensive API usage examples and reference
- **[Database Optimization](DATABASE_OPTIMIZATION.md)** - Performance tuning and indexing strategies
- **[Implementation Plan](IMPLEMENTATION_PLAN.md)** - Project development roadmap
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute to this project
- **[Swagger UI](http://localhost:8000/api/docs/)** - Interactive API documentation (when server is running)
- **[ReDoc](http://localhost:8000/api/redoc/)** - Alternative API documentation view

## Prerequisites

- Python 3.10+
- PostgreSQL 12+
- pip (Python package manager)

## Quick Start

### 1. Clone the repository

```bash
git clone <repository-url>
cd alx-e-commerce-backend
```

### 2. Create and activate virtual environment

```bash
# Windows
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Copy `.env.example` to `.env` and update with your configuration:

```bash
cp .env.example .env
```

Edit `.env` file:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=ecommerce_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
```

### 5. Create PostgreSQL database

```bash
# Log into PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE ecommerce_db;

# Exit
\q
```

### 6. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create superuser

```bash
python manage.py createsuperuser
```

### 8. Run development server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, access the API documentation:

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/swagger.json

## Project Structure

```
alx-e-commerce-backend/
├── apps/
│   ├── authentication/      # User authentication and management
│   ├── products/           # Product catalog management
│   └── core/              # Shared utilities and models
├── config/                # Project settings and configuration
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── media/                 # User-uploaded files
├── staticfiles/          # Collected static files
├── venv/                 # Virtual environment
├── .env                  # Environment variables (not in git)
├── .env.example          # Environment template
├── .gitignore
├── manage.py
├── requirements.txt
└── README.md
```

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login and get JWT tokens
- `POST /api/auth/refresh/` - Refresh access token
- `POST /api/auth/logout/` - Logout user
- `GET /api/auth/me/` - Get current user profile
- `PUT /api/auth/me/` - Update user profile

### Products
- `GET /api/products/` - List all products (with filters)
- `GET /api/products/{id}/` - Get product details
- `POST /api/products/` - Create new product (authenticated)
- `PUT /api/products/{id}/` - Update product (authenticated)
- `DELETE /api/products/{id}/` - Delete product (authenticated)

### Categories
- `GET /api/categories/` - List all categories
- `GET /api/categories/{id}/` - Get category details
- `POST /api/categories/` - Create category (admin only)
- `PUT /api/categories/{id}/` - Update category (admin only)
- `DELETE /api/categories/{id}/` - Delete category (admin only)

## Usage Examples

### Register a new user

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepass123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### Login

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "securepass123"
  }'
```

### Get products with filters

```bash
# Filter by category and sort by price
curl "http://localhost:8000/api/products/?category=electronics&ordering=price"

# Search products
curl "http://localhost:8000/api/products/?search=laptop"

# Pagination
curl "http://localhost:8000/api/products/?page=2&page_size=10"
```

## Development

### Running tests

```bash
python manage.py test
```

### Create migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Collect static files

```bash
python manage.py collectstatic
```

## Git Workflow

This project follows a structured commit workflow based on conventional commits:

```bash
feat: set up Django project with PostgreSQL
feat: implement user authentication with JWT
feat: add product APIs with filtering and pagination
feat: integrate Swagger documentation for API endpoints
perf: optimize database queries with indexing
docs: add API usage instructions in Swagger
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 📈 Performance

### Optimization Features

- **Database Indexing**: Strategic indexes on frequently queried fields
- **Query Optimization**: Using `select_related()` and `prefetch_related()`
- **Pagination**: Efficient data loading with configurable page sizes
- **Caching Ready**: Structure supports Redis/Memcached integration

See [DATABASE_OPTIMIZATION.md](DATABASE_OPTIMIZATION.md) for details.

## Deployment

### Production Checklist

- [ ] Set `DEBUG=False` in production
- [ ] Use a strong `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set up PostgreSQL with proper credentials
- [ ] Configure static/media file serving
- [ ] Set up HTTPS
- [ ] Configure CORS properly
- [ ] Enable database backups
- [ ] Set up logging
- [ ] Configure rate limiting
- [ ] Set up monitoring (New Relic, DataDog, etc.)

### Deployment Platforms

This API can be deployed on:
- **Heroku**: Easy deployment with PostgreSQL addon
- **Railway**: Modern platform with PostgreSQL support
- **DigitalOcean**: App Platform or Droplets
- **AWS**: EC2, RDS, and Elastic Beanstalk
- **Google Cloud**: App Engine or Compute Engine
- [ ] Configure rate limiting

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Contact

For questions or support, please contact: contact@ecommerce.local

## Acknowledgments

- Django Documentation
- Django REST Framework
- drf-yasg for API documentation
