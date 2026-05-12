from django.urls import re_path
from apps.home.views.web import index

urlpatterns = [
    re_path(r'^.*$', index),
]