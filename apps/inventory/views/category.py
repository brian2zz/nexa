from rest_framework import viewsets

from apps.inventory.models.category import (
    Category
)

from apps.inventory.serializers.category import (
    CategorySerializer
)


class CategoryViewSet(
    viewsets.ModelViewSet
):

    queryset = Category.objects.all()

    serializer_class = CategorySerializer