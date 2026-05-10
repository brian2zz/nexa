from rest_framework import viewsets

from apps.{{ app_name }}.models.{{ file_name }} import (
    {{ class_name }}
)

from apps.{{ app_name }}.serializers.{{ file_name }} import (
    {{ class_name }}Serializer
)


class {{ class_name }}ViewSet(
    viewsets.ModelViewSet
):

    queryset = {{ class_name }}.objects.all()

    serializer_class = {{ class_name }}Serializer