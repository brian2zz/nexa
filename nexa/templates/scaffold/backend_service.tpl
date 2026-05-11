from ..models.{{ file_name }} import {{ class_name }}

class {{ class_name }}Service:
    """
    Business logic layer for {{ class_name }}.
    Decouples database operations from views.
    """
    @staticmethod
    def get_all():
        return {{ class_name }}.objects.all()

    @staticmethod
    def get_by_id(obj_id):
        return {{ class_name }}.objects.filter(id=obj_id).first()

    @staticmethod
    def create(data):
        return {{ class_name }}.objects.create(**data)

    @staticmethod
    def update(obj_id, data):
        obj = {{ class_name }}.objects.filter(id=obj_id).first()
        if obj:
            for key, value in data.items():
                setattr(obj, key, value)
            obj.save()
        return obj

    @staticmethod
    def delete(obj_id):
        obj = {{ class_name }}.objects.filter(id=obj_id).first()
        if obj:
            obj.delete()
            return True
        return False
