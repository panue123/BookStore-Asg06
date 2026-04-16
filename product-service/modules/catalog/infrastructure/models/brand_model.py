from django.db import models


class BrandModel(models.Model):
    name     = models.CharField(max_length=100, unique=True)
    slug     = models.SlugField(max_length=100, unique=True)
    logo_url = models.URLField(blank=True)

    class Meta:
        db_table = 'brands'

    def __str__(self):
        return self.name
