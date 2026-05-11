def generate_model_fields(fields):

    lines = []

    type_map = {
        'string': (
            'models.CharField(max_length=255)'
        ),
        'text': (
            'models.TextField()'
        ),
        'int': (
            'models.IntegerField()'
        ),
        'bool': (
            'models.BooleanField(default=False)'
        ),
        'boolean': (
            'models.BooleanField(default=False)'
        ),
        'float': (
            'models.FloatField()'
        ),
        'date': (
            'models.DateField()'
        ),
        'datetime': (
            'models.DateTimeField()'
        ),
        'decimal': (
            'models.DecimalField(max_digits=10, decimal_places=2)'
        )
    }

    for field in fields:

        if ':' not in field:
            continue

        name, field_type = [part.strip() for part in field.split(':', 1)]

        django_field = type_map.get(field_type)

        if not django_field:
            continue

        lines.append(
            f'    {name} = {django_field}'
        )

    return '\n'.join(lines)