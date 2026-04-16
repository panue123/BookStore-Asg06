from django.contrib import admin
from modules.catalog.infrastructure.models.product_model import ProductModel
from modules.catalog.infrastructure.models.category_model import CategoryModel
from modules.catalog.infrastructure.models.variant_model import VariantModel
from modules.catalog.infrastructure.models.brand_model import BrandModel


@admin.register(CategoryModel)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug', 'parent', 'icon']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(ProductModel)
class ProductAdmin(admin.ModelAdmin):
    list_display  = ['id', 'name', 'category', 'price', 'stock', 'is_active']
    list_filter   = ['category', 'is_active']
    search_fields = ['name']


@admin.register(VariantModel)
class VariantAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'name', 'sku', 'price', 'stock']


@admin.register(BrandModel)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
