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

def translate_field(schema):
    """
    Translates a single FieldSchema into a Django model field line.
    """
    base_field = DJANGO_FIELD_MAP.get(schema.type)
    
    if not base_field:
        return None
        
    # Inject relationship info if needed
    if "{to}" in base_field:
        target = schema.to or "self"
        # Handle namespaced targets: "inventory.Category" -> "'inventory.Category'"
        if "." in target:
            target = f"'{target}'"
            
        base_field = base_field.format(
            to=target,
            on_delete=schema.on_delete or "CASCADE"
        )
        
    # Handling requirements without fragile .replace()
    # We strip the closing parenthesis and re-add it with extra options
    # Or better: check if there are options to add
    
    options = []
    
    if not schema.required:
        options.append("null=True")
        options.append("blank=True")
        
    if not options:
        return f"{schema.name} = {base_field}"
        
    # Constructing the field string more robustly
    # If base_field already has arguments, we add a comma
    clean_base = base_field.rstrip(')')
    separator = ", " if '(' in clean_base and clean_base[-1] != '(' else ""
    
    return f"{schema.name} = {clean_base}{separator}{', '.join(options)})"

def generate_django_fields(field_schemas):
    """
    Translates a list of FieldSchema objects into a block of Django code.
    """
    lines = []
    
    for schema in field_schemas:
        line = translate_field(schema)
        if line:
            lines.append(f'    {line}')
            
    return '\n'.join(lines)
