from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    admission_number = models.CharField(max_length=20, unique=True)
    grade = models.CharField(max_length=50)
    profile_picture = models.ImageField(upload_to='students/', blank=True, null=True)
    
    def __str__(self):
        return self.user.username
    
class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    profile_picture = models.ImageField(upload_to='teachers/', blank=True, null=True)

    def __str__(self):
        return self.user.username

class ParentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    students = models.ManyToManyField(StudentProfile, blank=True)
    def __str__(self):
        return self.user.username