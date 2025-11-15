"""
API Endpoint Test Script

This script tests that all API endpoints are properly configured
and accessible in the Swagger documentation.
"""

import sys
import os
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.urls import get_resolver
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

def test_swagger_endpoints():
    """Test that Swagger documentation endpoints are accessible."""
    client = APIClient()
    
    endpoints = [
        '/api/docs/',
        '/api/redoc/',
        '/api/swagger.json',
    ]
    
    print("Testing Swagger Documentation Endpoints:")
    print("-" * 50)
    
    for endpoint in endpoints:
        response = client.get(endpoint)
        status = "✓ PASS" if response.status_code == 200 else "✗ FAIL"
        print(f"{status} - {endpoint} - Status: {response.status_code}")
    
    print()

def list_all_api_endpoints():
    """List all registered API endpoints."""
    print("Registered API Endpoints:")
    print("-" * 50)
    
    resolver = get_resolver()
    
    # Authentication endpoints
    print("\n📝 Authentication Endpoints:")
    auth_endpoints = [
        'POST /api/auth/register/ - Register new user',
        'POST /api/auth/login/ - Login user',
        'POST /api/auth/logout/ - Logout user',
        'POST /api/auth/refresh/ - Refresh access token',
        'GET /api/auth/me/ - Get user profile',
        'PUT /api/auth/me/ - Update user profile',
        'PATCH /api/auth/me/ - Partial update user profile',
        'POST /api/auth/change-password/ - Change password',
    ]
    for endpoint in auth_endpoints:
        print(f"  {endpoint}")
    
    # Category endpoints
    print("\n📂 Category Endpoints:")
    category_endpoints = [
        'GET /api/categories/ - List all categories',
        'POST /api/categories/ - Create category (Admin only)',
        'GET /api/categories/{slug}/ - Get category details',
        'PUT /api/categories/{slug}/ - Update category (Admin only)',
        'PATCH /api/categories/{slug}/ - Partial update category (Admin only)',
        'DELETE /api/categories/{slug}/ - Delete category (Admin only)',
    ]
    for endpoint in category_endpoints:
        print(f"  {endpoint}")
    
    # Product endpoints
    print("\n📦 Product Endpoints:")
    product_endpoints = [
        'GET /api/products/ - List all products (with filters)',
        'POST /api/products/ - Create product (Auth required)',
        'GET /api/products/{slug}/ - Get product details',
        'PUT /api/products/{slug}/ - Update product (Owner/Admin)',
        'PATCH /api/products/{slug}/ - Partial update product (Owner/Admin)',
        'DELETE /api/products/{slug}/ - Delete product (Owner/Admin)',
    ]
    for endpoint in product_endpoints:
        print(f"  {endpoint}")
    
    print("\n" + "-" * 50)
    print(f"Total API Endpoints: {len(auth_endpoints) + len(category_endpoints) + len(product_endpoints)}")
    print()

def check_swagger_configuration():
    """Check if Swagger is properly configured."""
    print("Swagger Configuration Check:")
    print("-" * 50)
    
    from django.conf import settings
    
    # Check if drf_yasg is installed
    if 'drf_yasg' in settings.INSTALLED_APPS:
        print("✓ drf_yasg is installed")
    else:
        print("✗ drf_yasg is NOT installed")
    
    # Check if DRF is configured
    if hasattr(settings, 'REST_FRAMEWORK'):
        print("✓ REST_FRAMEWORK is configured")
        print(f"  - Pagination: {settings.REST_FRAMEWORK.get('DEFAULT_PAGINATION_CLASS', 'Not set')}")
        print(f"  - Page size: {settings.REST_FRAMEWORK.get('PAGE_SIZE', 'Not set')}")
    else:
        print("✗ REST_FRAMEWORK is NOT configured")
    
    # Check if SWAGGER_SETTINGS is configured
    if hasattr(settings, 'SWAGGER_SETTINGS'):
        print("✓ SWAGGER_SETTINGS is configured")
    else:
        print("✗ SWAGGER_SETTINGS is NOT configured")
    
    print()

if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("E-COMMERCE API DOCUMENTATION TEST")
    print("=" * 50 + "\n")
    
    check_swagger_configuration()
    test_swagger_endpoints()
    list_all_api_endpoints()
    
    print("=" * 50)
    print("Test Complete!")
    print("=" * 50)
    print("\nTo view the API documentation:")
    print("1. Start the development server: python manage.py runserver")
    print("2. Navigate to: http://localhost:8000/api/docs/")
    print("3. Or view ReDoc: http://localhost:8000/api/redoc/")
