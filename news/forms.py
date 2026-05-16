from django.db import models
from django import forms
from news.models import NewsPost

class NewsPostForm(forms.ModelForm):
    content = models.TextField()
    image = models.ImageField(upload_to='news_images/')
    
    class Meta:
        model = NewsPost
        fields = ['title', 'content', 'image']          
    