```markdown
# API Documentation Guide

## Overview

This document provides detailed information about the E-Commerce Backend API endpoints, authentication, request/response formats, and usage examples.

## Base URL

```
Development: http://localhost:8000
Production: https://your-domain.com
```

## Interactive Documentation

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/swagger.json

## Authentication

This API uses JWT (JSON Web Tokens) for authentication.

### Getting Tokens

**Register a new user:**
```http
POST /api/auth/register/
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "address": "123 Main St, City, Country"
}
```

**Response:**
```json
{
  "user": {
    "id": "uuid",
    "username": "john_doe",
    "email": "john@example.com",
    "full_name": "John Doe"
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  },
  "message": "User registered successfully"
}
```

**Login:**
```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "john_doe",
  "password": "SecurePass123!"
}
```

### Using Tokens

Include the access token in the Authorization header:

```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### Token Refresh

Access tokens expire after 15 minutes. Use the refresh token to get a new access token:

```http
POST /api/auth/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Logout

```http
POST /api/auth/logout/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

## API Endpoints

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register/` | Register new user | No |
| POST | `/api/auth/login/` | Login user | No |
| POST | `/api/auth/logout/` | Logout user | Yes |
| POST | `/api/auth/refresh/` | Refresh access token | No |
| GET | `/api/auth/me/` | Get current user profile | Yes |
| PUT/PATCH | `/api/auth/me/` | Update user profile | Yes |
| POST | `/api/auth/change-password/` | Change password | Yes |

### Category Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/categories/` | List all categories | No |
| GET | `/api/categories/{slug}/` | Get category details | No |
| POST | `/api/categories/` | Create category | Admin |
| PUT/PATCH | `/api/categories/{slug}/` | Update category | Admin |
| DELETE | `/api/categories/{slug}/` | Delete category | Admin |

### Product Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/products/` | List all products | No |
| GET | `/api/products/{slug}/` | Get product details | No |
| POST | `/api/products/` | Create product | Yes |
| PUT/PATCH | `/api/products/{slug}/` | Update product | Owner/Admin |
| DELETE | `/api/products/{slug}/` | Delete product | Owner/Admin |

## Filtering & Sorting

### Product Filters

**Filter by category:**
```
GET /api/products/?category=electronics
```

**Filter by price range:**
```
GET /api/products/?min_price=100&max_price=500
```

**Filter by stock availability:**
```
GET /api/products/?in_stock=true
```

**Search products:**
```
GET /api/products/?search=laptop
```

**Combine filters:**
```
GET /api/products/?category=electronics&min_price=100&max_price=1000&in_stock=true
```

### Sorting

**Sort by price (ascending):**
```
GET /api/products/?ordering=price
```

**Sort by price (descending):**
```
GET /api/products/?ordering=-price
```

**Sort by newest first:**
```
GET /api/products/?ordering=-created_at
```

**Sort by name:**
```
GET /api/products/?ordering=name
```

### Pagination

**Navigate pages:**
```
GET /api/products/?page=2
```

**Set page size:**
```
GET /api/products/?page_size=50
```

**Default page size:** 20 items

## Request/Response Examples

### Create a Product

**Request:**
```http
POST /api/products/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Wireless Bluetooth Headphones",
  "description": "High-quality wireless headphones with noise cancellation",
  "price": "149.99",
  "category": "uuid-of-category",
  "stock_quantity": 50,
  "is_active": true
}
```

**Response (201 Created):**
```json
{
  "id": "product-uuid",
  "name": "Wireless Bluetooth Headphones",
  "slug": "wireless-bluetooth-headphones",
  "description": "High-quality wireless headphones with noise cancellation",
  "price": "149.99",
  "category": {
    "id": "category-uuid",
    "name": "Electronics",
    "slug": "electronics"
  },
  "stock_quantity": 50,
  "in_stock": true,
  "availability_status": "In Stock",
  "image": null,
  "is_active": true,
  "created_by": "user-uuid",
  "created_by_username": "john_doe",
  "created_at": "2025-11-15T10:30:00Z",
  "updated_at": "2025-11-15T10:30:00Z"
}
```

... (truncated for brevity; full API guide is available in root `API_GUIDE.md`)
```
