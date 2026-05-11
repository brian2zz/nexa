from rest_framework import viewsets

from apps.warehouse.models.warehouse import (
    Warehouse
)

from apps.warehouse.serializers.warehouse import (
    WarehouseSerializer
)


class WarehouseViewSet(
    viewsets.ModelViewSet
):

    queryset = Warehouse.objects.all()

    serializer_class = WarehouseSerializer