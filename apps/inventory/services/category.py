from ..models.category import Category

class CategoryService:
    """
    Business logic layer for Category.
    Decouples database operations from views.
    """
    @staticmethod
    def get_all():
        return Category.objects.all()

    @staticmethod
    def get_by_id(obj_id):
        return Category.objects.filter(id=obj_id).first()

    @staticmethod
    def create(data):
        return Category.objects.create(**data)

    @staticmethod
    def update(obj_id, data):
        obj = Category.objects.filter(id=obj_id).first()
        if obj:
            for key, value in data.items():
                setattr(obj, key, value)
            obj.save()
        return obj

    @staticmethod
    def delete(obj_id):
        obj = Category.objects.filter(id=obj_id).first()
        if obj:
            obj.delete()
            return True
        return False
