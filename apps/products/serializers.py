from rest_framework import serializers
from .models import Product, Category


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for Category model.
    """
    product_count = serializers.ReadOnlyField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description', 'product_count', 
                  'created_at', 'updated_at')
        read_only_fields = ('id', 'slug', 'created_at', 'updated_at')


class ProductListSerializer(serializers.ModelSerializer):
    """
    Serializer for product list view with minimal fields.
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    in_stock = serializers.ReadOnlyField()
    availability_status = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = ('id', 'name', 'slug', 'price', 'category', 'category_name', 
                  'stock_quantity', 'in_stock', 'availability_status', 
                  'image', 'is_active', 'created_at')
        read_only_fields = ('id', 'slug', 'created_at')


class ProductDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for product detail view with all fields.
    """
    category = CategorySerializer(read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    in_stock = serializers.ReadOnlyField()
    availability_status = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = ('id', 'name', 'slug', 'description', 'price', 'category', 
                  'stock_quantity', 'in_stock', 'availability_status', 'image', 
                  'is_active', 'created_by', 'created_by_username', 
                  'created_at', 'updated_at')
        read_only_fields = ('id', 'slug', 'created_by', 'created_at', 'updated_at')


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating products.
    """
    class Meta:
        model = Product
        fields = ('name', 'description', 'price', 'category', 
                  'stock_quantity', 'image', 'is_active')

    def validate_price(self, value):
        """Ensure price is positive."""
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value

    def validate_stock_quantity(self, value):
        """Ensure stock quantity is non-negative."""
        if value < 0:
            raise serializers.ValidationError("Stock quantity cannot be negative.")
        return value

    def validate_name(self, value):
        """Ensure product name is not empty."""
        if not value.strip():
            raise serializers.ValidationError("Product name cannot be empty.")
        return value.strip()

    def create(self, validated_data):
        """Create product with the current user as creator."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
        return super().create(validated_data)
