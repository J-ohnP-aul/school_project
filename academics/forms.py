from django import forms

from .models import Assignment,Grade, Attendance
from accounts.models import StudentProfile

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = [
            'title',
            'description',
            'due_date'
        ]

        widgets = {

            'due_date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                }
            ),

            'title': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'description': forms.Textarea(
                attrs={
                    'class': 'form-control'
                }
            )
        }
class GradeForm(forms.ModelForm):

    class Meta:

        model = Grade

        fields = [
            'student',
            'assignment',
            'score',
            'remarks'
        ]

        widgets = {

            'student': forms.Select(
                attrs={'class': 'form-select'}
            ),

            'assignment': forms.Select(
                attrs={'class': 'form-select'}
            ),

            'score': forms.NumberInput(
                attrs={'class': 'form-control'}
            ),

            'remarks': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3
                }
            )
        }

class AttendanceForm(forms.ModelForm):

    class Meta:

        model = Attendance

        fields = [
            'student',
            'date',
            'status'
        ]

        widgets = {

            'student': forms.Select(
                attrs={'class': 'form-select'}
            ),

            'date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                }
            ),

            'status': forms.Select(
                attrs={'class': 'form-select'}
            )
        }