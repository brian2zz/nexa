from django.db import models


class {{ class_name }}(models.Model):

{{ model_fields }}

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):

        return self.name