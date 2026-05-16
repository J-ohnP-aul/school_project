from django.urls import path
from .views import admin_dashboard, register_view, login_view, logout_view, dashboard, users_list, aplicant_list

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    #admin pannel
    path('admin_dashboard/', admin_dashboard, name='admin_dashboard'),
    path('users_list/', users_list, name='users_list'),
    path('applicant_list/', aplicant_list, name='applicant_list'),
]