from django.db import models
from .category_model import CategoryModel
from .brand_model import BrandModel
from .product_type_model import ProductTypeModel


class ProductModel(models.Model):
    """
    Django ORM model cho Product tổng quát — hỗ trợ đa domain.
    attributes = JSONB — linh hoạt cho mọi loại sản phẩm.
    Ví dụ sách: {"author": "...", "pages": 320, "publisher": "NXB Trẻ"}
    Ví dụ điện tử: {"brand": "Samsung", "ram": "8GB", "storage": "256GB"}
    """
    name         = models.CharField(max_length=255, db_index=True)
    sku          = models.CharField(max_length=64, unique=True, blank=True, default="")
    category     = models.ForeignKey(CategoryModel, on_delete=models.PROTECT, related_name='products')
    brand        = models.ForeignKey(BrandModel, null=True, blank=True, on_delete=models.SET_NULL)
    product_type = models.ForeignKey(ProductTypeModel, null=True, blank=True, on_delete=models.SET_NULL)
    price        = models.DecimalField(max_digits=12, decimal_places=0)
    stock        = models.IntegerField(default=0)
    description  = models.TextField(blank=True)
    cover_image  = models.URLField(blank=True)
    attributes   = models.JSONField(default=dict)
    is_active    = models.BooleanField(default=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'
        ordering = ['-created_at']

    def __str__(self):
        return self.name
