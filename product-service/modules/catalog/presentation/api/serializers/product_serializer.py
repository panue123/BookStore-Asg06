from rest_framework import serializers
from ....infrastructure.models.product_model import ProductModel
from ....infrastructure.models.variant_model import VariantModel


class VariantSerializer(serializers.ModelSerializer):
    class Meta:
        model  = VariantModel
        fields = ['id', 'name', 'sku', 'price', 'stock', 'attributes']


class ProductSerializer(serializers.ModelSerializer):
    category_name    = serializers.CharField(source='category.name', read_only=True)
    category_slug    = serializers.CharField(source='category.slug', read_only=True)
    brand_name       = serializers.CharField(source='brand.name', read_only=True)
    product_type_name = serializers.CharField(source='product_type.name', read_only=True)
    variants         = VariantSerializer(many=True, read_only=True)

    class Meta:
        model  = ProductModel
        fields = [
            'id', 'name', 'sku', 'category', 'category_name', 'category_slug',
            'brand', 'brand_name', 'product_type', 'product_type_name',
            'price', 'stock', 'description', 'cover_image',
            'attributes', 'is_active', 'variants', 'created_at',
        ]
