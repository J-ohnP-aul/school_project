from django.urls import path

from academics import views
from .views import home, about, contact, gallery_view

urlpatterns = [
    path('', home, name='home'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('gallery/', gallery_view, name='gallery'),
]
