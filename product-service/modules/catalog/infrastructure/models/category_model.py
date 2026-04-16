from django.db import models


class CategoryModel(models.Model):
    """
    Category là dữ liệu trong DB — 12 danh mục sách tiếng Việt.
    Không phải enum cứng trong code.
    """
    name        = models.CharField(max_length=100, unique=True)
    slug        = models.SlugField(max_length=100, unique=True)
    parent      = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children')
    description = models.TextField(blank=True)
    icon        = models.CharField(max_length=10, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'categories'
        ordering = ['name']

    def __str__(self):
        return self.name
