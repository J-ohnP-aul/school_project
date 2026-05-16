from django import forms
from django.db import models

from .models import GalleryImage

class GalleryImgForm(forms.ModelForm):
    class Meta:
        model = GalleryImage
        fields = ['title', 'description', 'image']