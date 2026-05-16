from django.urls import path
from .views import admin_dashboard, register_view, login_view, logout_view, dashboard, users_list, aplicant_list, complete_profile, search_students, delete_user, delete_applicant, create_user

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('complete-profile/<str:role>/', complete_profile, name='complete_profile'),
    path('search-students/', search_students, name='search_students'),
    #admin pannel
    path('admin_dashboard/', admin_dashboard, name='admin_dashboard'),
    path('users_list/', users_list, name='users_list'),
    path('users/<int:pk>/delete/', delete_user, name='delete_user'),
    path('create-user/', create_user, name='create_user'),
    path('applicant_list/', aplicant_list, name='applicant_list'),
    path('applicants/<int:pk>/delete/', delete_applicant, name='delete_applicant'),
]