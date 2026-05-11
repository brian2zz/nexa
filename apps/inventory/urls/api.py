from apps.inventory.views.category import CategoryViewSet
from apps.inventory.views.product import ProductViewSet
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
]
