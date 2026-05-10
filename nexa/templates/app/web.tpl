from django.urls import re_path
from apps.{{ app_name }}.views.web import index

urlpatterns = [
    re_path(r'^.*$', index),
]