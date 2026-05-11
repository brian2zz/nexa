from rest_framework import serializers

from apps.inventory.models.product import (
    Product
)


class ProductSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = Product

        fields = '__all__'