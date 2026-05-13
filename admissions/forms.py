from django import forms
from .models import Applicant

class ApplicantForm(forms.ModelForm):
    class Meta:
        model = Applicant
        fields = '__all__'
        widgets = {
            'date_of_birth': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                }
            ),
            'first_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter first name', # Moved inside attrs
                }
            ),
            'last_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter last name', # Moved inside attrs
                }
            ),
            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter email',
                }
            ),
            'phone': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter phone number',
                }
            ),
            'applying_grade': forms.Select(
                attrs={'class': 'form-select'},
            ),
            'previous_school': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter previous school',
                }
            ),
            'statement': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 5,
                    'placeholder': 'Enter statement',
                }
            ),
            'document': forms.ClearableFileInput(
                attrs={'class': 'form-control'},
            ),
        }