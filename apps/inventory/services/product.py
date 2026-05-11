from ..models.product import Product

class ProductService:
    """
    Business logic layer for Product.
    Decouples database operations from views.
    """
    @staticmethod
    def get_all():
        return Product.objects.all()

    @staticmethod
    def get_by_id(obj_id):
        return Product.objects.filter(id=obj_id).first()

    @staticmethod
    def create(data):
        return Product.objects.create(**data)

    @staticmethod
    def update(obj_id, data):
        obj = Product.objects.filter(id=obj_id).first()
        if obj:
            for key, value in data.items():
                setattr(obj, key, value)
            obj.save()
        return obj

    @staticmethod
    def delete(obj_id):
        obj = Product.objects.filter(id=obj_id).first()
        if obj:
            obj.delete()
            return True
        return False
