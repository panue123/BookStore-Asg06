from django.db import models
from .product_model import ProductModel


class VariantModel(models.Model):
    product    = models.ForeignKey(ProductModel, on_delete=models.CASCADE, related_name='variants')
    name       = models.CharField(max_length=100)   # "Bìa cứng", "Bìa mềm"
    sku        = models.CharField(max_length=64, unique=True)
    price      = models.DecimalField(max_digits=12, decimal_places=0)
    stock      = models.IntegerField(default=0)
    attributes = models.JSONField(default=dict)

    class Meta:
        db_table = 'product_variants'

    def __str__(self):
        return f"{self.product.name} — {self.name}"
