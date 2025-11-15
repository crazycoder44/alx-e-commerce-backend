from rest_framework import viewsets, filters, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Product, Category
from .serializers import (
    ProductListSerializer,
    ProductDetailSerializer,
    ProductCreateUpdateSerializer,
    CategorySerializer
)
from .filters import ProductFilter
from .permissions import IsOwnerOrReadOnly


class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing product categories.
    
    list: Get all categories
    retrieve: Get a single category
    create: Create a new category (admin only)
    update: Update a category (admin only)
    partial_update: Partially update a category (admin only)
    destroy: Delete a category (admin only)
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    
    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_description="Get list of all categories",
        responses={200: CategorySerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Get category details",
        responses={200: CategorySerializer()}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new category (admin only)",
        request_body=CategorySerializer,
        responses={201: CategorySerializer()}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update a category (admin only)",
        request_body=CategorySerializer,
        responses={200: CategorySerializer()}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Partially update a category (admin only)",
        request_body=CategorySerializer,
        responses={200: CategorySerializer()}
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete a category (admin only)",
        responses={204: "No content"}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing products with filtering, sorting, and pagination.
    
    Filtering:
    - ?category=<slug> - Filter by category slug
    - ?min_price=<amount> - Filter by minimum price
    - ?max_price=<amount> - Filter by maximum price
    - ?in_stock=true/false - Filter by stock availability
    - ?search=<query> - Search in product name and description
    
    Sorting:
    - ?ordering=price - Sort by price ascending
    - ?ordering=-price - Sort by price descending
    - ?ordering=-created_at - Sort by newest first
    - ?ordering=name - Sort by name alphabetically
    
    Pagination:
    - ?page=<number> - Page number
    - ?page_size=<number> - Items per page (max 100)
    """
    queryset = Product.objects.select_related('category', 'created_by').filter(is_active=True)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'created_at', 'stock_quantity']
    ordering = ['-created_at']
    lookup_field = 'slug'

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return ProductListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        return ProductDetailSerializer

    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Optionally restricts the returned products.
        Admins can see all products, others see only active ones.
        """
        queryset = Product.objects.select_related('category', 'created_by')
        
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
        
        return queryset

    @swagger_auto_schema(
        operation_description="""
        Get list of products with filtering and sorting options.
        
        **Filters:**
        - category: Filter by category slug
        - min_price: Minimum price
        - max_price: Maximum price
        - in_stock: true/false
        - search: Search in name and description
        
        **Sorting:**
        - ordering: name, -name, price, -price, created_at, -created_at
        
        **Example:** ?category=electronics&min_price=100&ordering=-price
        """,
        manual_parameters=[
            openapi.Parameter('category', openapi.IN_QUERY, description="Filter by category slug", type=openapi.TYPE_STRING),
            openapi.Parameter('min_price', openapi.IN_QUERY, description="Minimum price", type=openapi.TYPE_NUMBER),
            openapi.Parameter('max_price', openapi.IN_QUERY, description="Maximum price", type=openapi.TYPE_NUMBER),
            openapi.Parameter('in_stock', openapi.IN_QUERY, description="Filter by stock availability", type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('search', openapi.IN_QUERY, description="Search in name and description", type=openapi.TYPE_STRING),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Sort by field (prefix with - for descending)", type=openapi.TYPE_STRING),
            openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Items per page", type=openapi.TYPE_INTEGER),
        ],
        responses={200: ProductListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Get detailed product information",
        responses={200: ProductDetailSerializer()}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new product (requires authentication)",
        request_body=ProductCreateUpdateSerializer,
        responses={201: ProductDetailSerializer()}
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        return Response(
            ProductDetailSerializer(product).data,
            status=status.HTTP_201_CREATED
        )

    @swagger_auto_schema(
        operation_description="Update a product (owner or admin only)",
        request_body=ProductCreateUpdateSerializer,
        responses={200: ProductDetailSerializer()}
    )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        return Response(ProductDetailSerializer(product).data)

    @swagger_auto_schema(
        operation_description="Partially update a product (owner or admin only)",
        request_body=ProductCreateUpdateSerializer,
        responses={200: ProductDetailSerializer()}
    )
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete a product (owner or admin only)",
        responses={204: "No content"}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Get products by category",
        responses={200: ProductListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], url_path='by-category/(?P<category_slug>[^/.]+)')
    def by_category(self, request, category_slug=None):
        """Get all products in a specific category."""
        products = self.get_queryset().filter(category__slug=category_slug)
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
