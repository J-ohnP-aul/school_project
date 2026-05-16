from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import RegisterForm 
from admissions.models import Applicant
from django.contrib.auth.models import User

# Create your views here.
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful. You can now log in.')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'logout successfull !!')
    return redirect('home')


@login_required
def dashboard(request):

    user = request.user
    is_student = user.groups.filter(name='Students').exists()
    is_teacher = user.groups.filter(name='Teachers').exists()
    is_parent = user.groups.filter(name='Parents').exists()
    context = {
        'is_student': is_student,
        'is_teacher': is_teacher,
        'is_parent': is_parent,
    }

    return render(
        request,
        'accounts/dashboard.html',
        context
    )
 
# admin dashboard and functionalities

context = {
    'users': User.objects.all(),
    'students': User.objects.filter(groups__name='Students').distinct(),
    'teachers': User.objects.filter(groups__name='Teachers').distinct(),
    'parents':  User.objects.filter(groups__name='Parents').distinct(),
}
 
@login_required   
def admin_dashboard(request):
    return render(request, 'accounts/admin_dashboard.html', context)

@login_required
def users_list(request):
    return render(request, 'accounts/partials/users_list.html', context)

def aplicant_list(request):
    applicants = Applicant.objects.all()
    return render(request, 'accounts/partials/applicant_list.html', {'applicants': applicants})