from django.urls import path
from .views import admin_login, admin_logout, admin_dashboard, aplicant_list, delete_applicant, applicant_detail

urlpatterns = [
    # Admin authentication
    path('admin-login/', admin_login, name='admin_login'),
    path('admin-logout/', admin_logout, name='admin_logout'),
    # Admin dashboard
    path('admin_dashboard/', admin_dashboard, name='admin_dashboard'),
    # Applicant management
    path('applicant_list/', aplicant_list, name='applicant_list'),
    path('applicants/<int:pk>/', applicant_detail, name='applicant_detail'),
    path('applicants/<int:pk>/delete/', delete_applicant, name='delete_applicant'),
]