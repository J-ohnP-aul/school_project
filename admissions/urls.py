from django.urls import path
from .views import apply

urlpatterns = [
    path('', apply, name='apply'),
]