from django.db import models
from django.conf import settings
from django.utils.text import slugify
import uuid


class Category(models.Model):
    """
    Product category model.
    Organizes products into hierarchical categories.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name'], name='category_name_idx'),
            models.Index(fields=['slug'], name='category_slug_idx'),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def product_count(self):
        """Returns the number of products in this category."""
        return self.products.filter(is_active=True).count()


class Product(models.Model):
    """
    Product model representing items available in the e-commerce store.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price in USD"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='products'
    )
    stock_quantity = models.IntegerField(default=0)
    image = models.ImageField(
        upload_to='products/%Y/%m/%d/',
        blank=True,
        null=True
    )
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='products_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']
        indexes = [
            # Single field indexes
            models.Index(fields=['category'], name='product_category_idx'),
            models.Index(fields=['price'], name='product_price_idx'),
            models.Index(fields=['-created_at'], name='product_created_idx'),
            models.Index(fields=['slug'], name='product_slug_idx'),
            models.Index(fields=['is_active'], name='product_active_idx'),
            models.Index(fields=['stock_quantity'], name='product_stock_idx'),
            
            # Composite indexes for common query patterns
            models.Index(fields=['is_active', 'category'], name='product_active_cat_idx'),
            models.Index(fields=['is_active', 'price'], name='product_active_price_idx'),
            models.Index(fields=['is_active', '-created_at'], name='product_active_created_idx'),
            models.Index(fields=['category', 'price'], name='product_cat_price_idx'),
            models.Index(fields=['category', '-created_at'], name='product_cat_created_idx'),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def in_stock(self):
        """Check if product is in stock."""
        return self.stock_quantity > 0

    @property
    def availability_status(self):
        """Return availability status."""
        if self.stock_quantity == 0:
            return "Out of Stock"
        elif self.stock_quantity < 10:
            return "Low Stock"
        return "In Stock"
