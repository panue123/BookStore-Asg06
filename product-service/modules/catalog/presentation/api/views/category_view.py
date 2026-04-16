from rest_framework import viewsets
from ....infrastructure.models.category_model import CategoryModel
from ..serializers.category_serializer import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset         = CategoryModel.objects.all()
    serializer_class = CategorySerializer
