from django.urls import path

from academics import views
from .views import home, about, contact, gallery_view, gallery_del, gallery_create

urlpatterns = [
    path('', home, name='home'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('gallery_create/', gallery_create, name='gallery_create'),    #admin galore func
    path('gallery/', gallery_view, name='gallery'),
    path('gallery/delete/<int:pk>/', gallery_del, name='gallery_del'),
    
]
