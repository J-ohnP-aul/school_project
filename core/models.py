from django.db import models

# Create your models here.
class SchoolInfo(models.Model):
    name = models.CharField(max_length=200)
    mission = models.TextField()
    vision = models.TextField()
    history = models.TextField()

    def __str__(self):
        return self.name

class SchoolInfo(models.Model):
    name = models.CharField(max_length=200)
    mission = models.TextField()
    vision = models.TextField()
    history = models.TextField()

    def __str__(self):
        return self.name


class Staff(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    bio = models.TextField()
    photo = models.ImageField(upload_to='staff_photos/')

    def __str__(self):
        return self.name


class Facility(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='facilities/')

    def __str__(self):
        return self.title
    
class GalleryImage(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='gallery/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title