"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger schema view with comprehensive API documentation
schema_view = get_schema_view(
    openapi.Info(
        title="E-Commerce Backend API",
        default_version='v1',
        description="""
# E-Commerce Backend API Documentation

A comprehensive RESTful API for e-commerce applications featuring:

## Features
* 🔐 **JWT Authentication** - Secure user registration and login
* 📦 **Product Management** - Full CRUD operations for products and categories
* 🔍 **Advanced Filtering** - Filter by category, price range, and stock availability
* 📊 **Sorting & Pagination** - Efficient data retrieval with customizable sorting
* 🔒 **Permission-based Access** - Owner and admin-level permissions
* 📚 **Comprehensive Documentation** - Interactive API documentation

## Authentication
This API uses JWT (JSON Web Tokens) for authentication. To access protected endpoints:
1. Register a new account at `/api/auth/register/`
2. Login at `/api/auth/login/` to receive access and refresh tokens
3. Include the access token in the Authorization header: `Bearer <token>`
4. Use `/api/auth/refresh/` to get a new access token when it expires

## Getting Started
1. Register a new user account
2. Login to receive JWT tokens
3. Use the "Authorize" button above to add your token
4. Start exploring the API endpoints

For detailed examples and usage guide, see the [API Guide](https://github.com/crazycoder44/alx-e-commerce-backend/blob/main/API_GUIDE.md)
        """,
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(
            name="E-Commerce API Support",
            email="contact@ecommerce.local",
            url="https://github.com/crazycoder44/alx-e-commerce-backend"
        ),
        license=openapi.License(
            name="MIT License",
            url="https://opensource.org/licenses/MIT"
        ),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/auth/', include('apps.authentication.urls')),
    path('api/', include('apps.products.urls')),
    
    # API Documentation
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

