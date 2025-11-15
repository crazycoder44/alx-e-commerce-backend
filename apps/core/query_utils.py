"""
Query Optimization Utilities

This module provides utilities for analyzing and optimizing database queries.
"""

from django.db import connection
from django.db.models import Q, Prefetch
import time
from functools import wraps


def query_debugger(func):
    """
    Decorator to print query count and execution time for a function.
    Useful for identifying N+1 query problems.
    
    Usage:
        @query_debugger
        def my_view(request):
            # Your code here
            pass
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Reset queries
        from django.conf import settings
        debug_state = settings.DEBUG
        settings.DEBUG = True
        
        # Clear query log
        connection.queries_log.clear()
        
        # Start timing
        start_time = time.time()
        
        # Execute function
        result = func(*args, **kwargs)
        
        # End timing
        end_time = time.time()
        
        # Calculate metrics
        num_queries = len(connection.queries)
        total_time = sum(float(q['time']) for q in connection.queries)
        execution_time = end_time - start_time
        
        # Print results
        print(f"\n{'='*60}")
        print(f"Function: {func.__name__}")
        print(f"{'='*60}")
        print(f"Number of queries: {num_queries}")
        print(f"Total query time: {total_time:.4f}s")
        print(f"Total execution time: {execution_time:.4f}s")
        print(f"{'='*60}\n")
        
        # Restore debug state
        settings.DEBUG = debug_state
        
        return result
    return wrapper


def print_queries():
    """
    Print all queries executed so far in the current request.
    Useful for debugging in Django shell or views.
    """
    print(f"\nTotal queries: {len(connection.queries)}\n")
    for i, query in enumerate(connection.queries, 1):
        print(f"Query {i}:")
        print(f"Time: {query['time']}s")
        print(f"SQL: {query['sql']}\n")


def analyze_queryset(queryset):
    """
    Analyze a queryset and provide optimization suggestions.
    
    Args:
        queryset: Django QuerySet to analyze
        
    Returns:
        dict: Analysis results with suggestions
    """
    analysis = {
        'model': queryset.model.__name__,
        'count': queryset.count(),
        'query': str(queryset.query),
        'suggestions': []
    }
    
    # Check for select_related usage
    if hasattr(queryset, 'query') and hasattr(queryset.query, 'select_related'):
        if not queryset.query.select_related:
            analysis['suggestions'].append(
                "Consider using select_related() for ForeignKey relationships"
            )
    
    # Check for prefetch_related usage
    if hasattr(queryset, '_prefetch_related_lookups'):
        if not queryset._prefetch_related_lookups:
            analysis['suggestions'].append(
                "Consider using prefetch_related() for reverse ForeignKey or ManyToMany"
            )
    
    return analysis


class QueryCounter:
    """
    Context manager to count queries executed within a block.
    
    Usage:
        with QueryCounter() as qc:
            # Your code here
            products = Product.objects.all()
        
        print(f"Queries executed: {qc.count}")
    """
    
    def __init__(self):
        self.count = 0
        self.start_count = 0
    
    def __enter__(self):
        self.start_count = len(connection.queries)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.count = len(connection.queries) - self.start_count


def optimize_product_queries():
    """
    Returns optimized querysets for common Product queries.
    
    Returns:
        dict: Dictionary of optimized querysets
    """
    from apps.products.models import Product, Category
    
    return {
        'active_products': Product.objects.select_related(
            'category', 'created_by'
        ).filter(is_active=True),
        
        'products_with_category': Product.objects.select_related('category'),
        
        'products_by_category': lambda category_slug: Product.objects.select_related(
            'category', 'created_by'
        ).filter(category__slug=category_slug, is_active=True),
        
        'in_stock_products': Product.objects.select_related(
            'category'
        ).filter(stock_quantity__gt=0, is_active=True),
        
        'categories_with_products': Category.objects.prefetch_related(
            Prefetch(
                'products',
                queryset=Product.objects.filter(is_active=True).select_related('category')
            )
        ),
    }


def bulk_operations_example():
    """
    Examples of efficient bulk operations.
    These are significantly faster than individual operations in loops.
    """
    from apps.products.models import Product
    
    # GOOD: Bulk create (single query)
    products = [
        Product(name=f"Product {i}", price=10.00)
        for i in range(100)
    ]
    Product.objects.bulk_create(products)
    
    # GOOD: Bulk update (single query)
    Product.objects.filter(stock_quantity=0).update(is_active=False)
    
    # BAD: Individual updates (100 queries)
    # for product in Product.objects.filter(stock_quantity=0):
    #     product.is_active = False
    #     product.save()


def efficient_exists_check():
    """
    Examples of efficient existence checks.
    """
    from apps.products.models import Product
    
    # GOOD: Use exists() for boolean checks
    has_products = Product.objects.filter(stock_quantity__gt=0).exists()
    
    # BAD: Using count() for existence check
    # has_products = Product.objects.filter(stock_quantity__gt=0).count() > 0
    
    # GOOD: Use first() to get one object or None
    product = Product.objects.filter(slug='example').first()
    
    # BAD: Using try/except with get()
    # try:
    #     product = Product.objects.get(slug='example')
    # except Product.DoesNotExist:
    #     product = None


def query_optimization_tips():
    """
    Print query optimization tips.
    """
    tips = """
    
    DATABASE QUERY OPTIMIZATION TIPS
    =================================
    
    1. SELECT RELATED (Forward Relations)
       Use for ForeignKey and OneToOneField:
       Product.objects.select_related('category', 'created_by')
    
    2. PREFETCH RELATED (Reverse Relations)
       Use for reverse ForeignKey and ManyToMany:
       Category.objects.prefetch_related('products')
    
    3. ONLY & DEFER
       Fetch specific fields:
       Product.objects.only('name', 'price')
       Product.objects.defer('description')
    
    4. VALUES & VALUES_LIST
       Get dictionaries or tuples instead of model instances:
       Product.objects.values('name', 'price')
       Product.objects.values_list('name', flat=True)
    
    5. ANNOTATE & AGGREGATE
       Perform database-level calculations:
       Category.objects.annotate(product_count=Count('products'))
    
    6. EXISTS vs COUNT
       For boolean checks, use exists():
       Product.objects.filter(price__gt=100).exists()
    
    7. BULK OPERATIONS
       Use bulk_create() and bulk_update() for multiple objects:
       Product.objects.bulk_create([product1, product2, ...])
    
    8. F EXPRESSIONS
       For field-based updates:
       Product.objects.update(price=F('price') * 1.1)
    
    9. Q OBJECTS
       For complex queries:
       Product.objects.filter(Q(price__lt=10) | Q(stock_quantity=0))
    
    10. RAW SQL
        For complex queries that Django ORM can't handle efficiently:
        Product.objects.raw('SELECT * FROM products WHERE ...')
    
    """
    print(tips)


if __name__ == '__main__':
    query_optimization_tips()
