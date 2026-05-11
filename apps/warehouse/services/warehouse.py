from ..models.warehouse import Warehouse

class WarehouseService:
    """
    Business logic layer for Warehouse.
    Decouples database operations from views.
    """
    @staticmethod
    def get_all():
        return Warehouse.objects.all()

    @staticmethod
    def get_by_id(obj_id):
        return Warehouse.objects.filter(id=obj_id).first()

    @staticmethod
    def create(data):
        return Warehouse.objects.create(**data)

    @staticmethod
    def update(obj_id, data):
        obj = Warehouse.objects.filter(id=obj_id).first()
        if obj:
            for key, value in data.items():
                setattr(obj, key, value)
            obj.save()
        return obj

    @staticmethod
    def delete(obj_id):
        obj = Warehouse.objects.filter(id=obj_id).first()
        if obj:
            obj.delete()
            return True
        return False
