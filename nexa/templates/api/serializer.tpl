from rest_framework import serializers

from apps.{{ app_name }}.models.{{ file_name }} import (
    {{ class_name }}
)


class {{ class_name }}Serializer(
    serializers.ModelSerializer
):

    class Meta:

        model = {{ class_name }}

        fields = '__all__'