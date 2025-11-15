import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    """
    Filter class for Product model.
    Provides filtering by category, price range, and stock availability.
    """
    category = django_filters.CharFilter(field_name='category__slug', lookup_expr='iexact')
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    in_stock = django_filters.BooleanFilter(method='filter_in_stock')
    
    class Meta:
        model = Product
        fields = ['category', 'min_price', 'max_price', 'in_stock']
    
    def filter_in_stock(self, queryset, name, value):
        """Filter products based on stock availability."""
        if value:
            return queryset.filter(stock_quantity__gt=0)
        return queryset.filter(stock_quantity=0)
