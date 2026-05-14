from django.urls import path

from .views import (
    create_assignment,
    assignment_list
)

urlpatterns = [
    path('', assignment_list, name='assignment_list' ),
    path('create/',create_assignment,name='create_assignment'),
]