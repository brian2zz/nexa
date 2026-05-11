from django.urls import path, include

urlpatterns = [
    path(
        'api/v1/warehouse/',
        include('apps.warehouse.urls.api')
    ),

    path(
        'api/v1/inventory/',
        include('apps.inventory.urls.api')
    ),

]
