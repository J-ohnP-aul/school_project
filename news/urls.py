from django.urls import path
from .views import news_del, news_list, news_detail, news_create

urlpatterns = [
    path('create/', news_create, name='news_create'),
    path('', news_list, name='news_list'),
    path('<slug:slug>/', news_detail, name='news_detail'),
    #admin post ctr
    path('delete/<int:pk>/', news_del, name='news_del'),
]