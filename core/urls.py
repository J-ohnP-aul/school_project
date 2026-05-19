from django.urls import path

from .views import home, about, contact, gallery_view, gallery_del, gallery_create, gallery_update ,facilities, facility_del, facility_create, facility_update

urlpatterns = [
    path('', home, name='home'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('facilities/', facilities, name='facilities'),
    path('facilities/create/', facility_create, name='facility_create'),
    path('facilities/delete/<int:pk>/', facility_del, name='facility_del'),
    path('facilities/update/<int:pk>/', facility_update, name='facility_update'),
    path('gallery_create/', gallery_create, name='gallery_create'),    # admin gallery management
    path('gallery/', gallery_view, name='gallery'),
    path('gallery/update/<int:pk>/', gallery_update, name='gallery_update'),
    path('gallery/delete/<int:pk>/', gallery_del, name='gallery_del'),
]
