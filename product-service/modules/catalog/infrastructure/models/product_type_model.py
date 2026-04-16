from django.db import models


class ProductTypeModel(models.Model):
    name             = models.CharField(max_length=100, unique=True)
    attribute_schema = models.JSONField(default=dict)  # {"author": "str", "pages": "int"}

    class Meta:
        db_table = 'product_types'

    def __str__(self):
        return self.name
