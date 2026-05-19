from django import forms
from django.db import models

from .models import GalleryImage, Facility

class GalleryImgForm(forms.ModelForm):
    class Meta:
        model = GalleryImage
        fields = ['title', 'description', 'image']
        
class FacilityForm(forms.ModelForm):
    class Meta:
        model = Facility
        fields = ['title', 'description', 'image']