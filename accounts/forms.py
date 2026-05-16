from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import StudentProfile, TeacherProfile, ParentProfile


class RegisterForm(UserCreationForm):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('parent', 'Parent'),
    )

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        required=True,
        widget=forms.RadioSelect(attrs={'class': 'auth-role-input'}),
        label='Register as'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class AdminCreateUserForm(UserCreationForm):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('parent', 'Parent'),
    )

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        required=True,
        widget=forms.RadioSelect(attrs={'class': 'auth-role-input'}),
        label='Account type'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['admission_number', 'grade', 'profile_picture']


class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = TeacherProfile
        fields = ['subject', 'profile_picture']


class ParentProfileForm(forms.ModelForm):
    students = forms.ModelMultipleChoiceField(
        queryset=StudentProfile.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'id': 'id_students', 'style': 'display:none;'})
    )

    class Meta:
        model = ParentProfile
        fields = ['phone', 'students']