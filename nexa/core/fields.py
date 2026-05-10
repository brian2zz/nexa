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
        'float': (
            'models.FloatField()'
        )
    }

    for field in fields:

        if ':' not in field:
            continue

        name, field_type = field.split(':')

        django_field = type_map.get(field_type)

        if not django_field:
            continue

        lines.append(
            f'    {name} = {django_field}'
        )

    return '\n'.join(lines)