from django.db import models
from django import forms

# Create your models here.
class Applicant(models.Model):

    GRADE_CHOICES = [
        ('Grade 1', 'Grade 1'),
        ('Grade 2', 'Grade 2'),
        ('Grade 3', 'Grade 3'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    email = models.EmailField()
    phone = models.CharField(max_length=20)

    date_of_birth = models.DateField()

    applying_grade = models.CharField(
        max_length=20,
        choices=GRADE_CHOICES
    )

    previous_school = models.CharField(max_length=200)

    statement = models.TextField()

    document = models.FileField(
        upload_to='applications/'
    )

    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class ApplicantForm(forms.ModelForm):
    class Meta:
        model = Applicant
        fields = '__all__'
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }