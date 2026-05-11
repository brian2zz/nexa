from rest_framework import viewsets

from apps.inventory.models.product import (
    Product
)

from apps.inventory.serializers.product import (
    ProductSerializer
)


class ProductViewSet(
    viewsets.ModelViewSet
):

    queryset = Product.objects.all()

    serializer_class = ProductSerializer