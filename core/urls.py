from django.urls import path

from academics import views
from .views import home, about, contact, gallery_view, gallery_del

urlpatterns = [
    path('', home, name='home'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('gallery/', gallery_view, name='gallery'),
    #admin galore func
    path('gallery/delete/<int:pk>/', gallery_del, name='gallery_del'),
    
]
