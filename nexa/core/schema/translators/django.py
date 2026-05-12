# nexa/core/schema/translators/django.py

DJANGO_FIELD_MAP = {
    'string': 'models.CharField(max_length=255)',
    'text': 'models.TextField()',
    'int': 'models.IntegerField()',
    'integer': 'models.IntegerField()',
    'bool': 'models.BooleanField(default=False)',
    'boolean': 'models.BooleanField(default=False)',
    'float': 'models.FloatField()',
    'date': 'models.DateField()',
    'datetime': 'models.DateTimeField()',
    'decimal': 'models.DecimalField(max_digits=10, decimal_places=2)',
    'foreignkey': 'models.ForeignKey({to}, on_delete=models.{on_delete})',
    'manytomany': 'models.ManyToManyField({to})',
    'onetoone': 'models.OneToOneField({to}, on_delete=models.{on_delete})'
}

def translate_field(schema, app_name=None):
    """
    Translates a single FieldSchema into a Django model field line.
    """
    base_field = DJANGO_FIELD_MAP.get(schema.type)
    
    if not base_field:
        return None
        
    # Inject relationship info if needed
    if "{to}" in base_field:
        target = schema.to or "self"
        
        # Force string reference for relationships to avoid import issues
        if target != "self" and "." not in target and app_name:
            target = f"{app_name}.{target}"
            
        if target != "self":
            target = f"'{target}'"
            
        base_field = base_field.format(
            to=target,
            on_delete=schema.on_delete or "CASCADE"
        )
        
    options = []
    
    # Intelligent relationship handling
    if schema.on_delete == "SET_NULL":
        options.append("null=True")
        options.append("blank=True")
    elif not schema.required:
        options.append("null=True")
        options.append("blank=True")

    if schema.related_name:
        options.append(f"related_name='{schema.related_name}'")
        
    if not options:
        return f"{schema.name} = {base_field}"
        
    clean_base = base_field.rstrip(')')
    separator = ", " if '(' in clean_base and clean_base[-1] != '(' else ""
    
    return f"{schema.name} = {clean_base}{separator}{', '.join(options)})"

def generate_django_fields(field_schemas, app_name=None):
    """
    Translates a list of FieldSchema objects into a block of Django code.
    """
    lines = []
    
    for schema in field_schemas:
        line = translate_field(schema, app_name=app_name)
        if line:
            lines.append(f'    {line}')
            
    return '\n'.join(lines)
