from django.contrib import admin

from django.contrib import admin
from .models import Product, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'product_type', 'price', 'sku', 'is_available', 'created_at']
    list_filter = ['product_type', 'is_available', 'created_at']
    search_fields = ['title', 'sku', 'description']
    list_editable = ['price', 'is_available']

admin.site.site_header = "Planner Shop Administration"