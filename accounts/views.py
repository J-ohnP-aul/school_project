from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.http import require_http_methods

from admissions.models import Applicant
from django.contrib.auth.models import User, Group


def get_user_role(user):
    if user.groups.filter(name='Students').exists():
        return 'student'
    if user.groups.filter(name='Teachers').exists():
        return 'teacher'
    if user.groups.filter(name='Parents').exists():
        return 'parent'
    return None



# ═══════════════════════════════════════════════════════════════
# ADMIN LOGIN (FOR STAFF/SUPERUSERS ONLY)
# ═══════════════════════════════════════════════════════════════

def admin_login(request):
    """Admin login view - staff and superusers only."""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_staff or user.is_superuser:
                login(request, user)
                messages.success(request, f'Welcome, {user.first_name or user.username}!')
                return redirect('admin_dashboard')
            else:
                messages.error(request, 'You do not have admin access.')
        else:
            messages.error(request, 'Invalid credentials.')
    
    return render(request, 'accounts/admin_login.html')


def admin_logout(request):
    """Admin logout."""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')


# ═══════════════════════════════════════════════════════════════
# PUBLIC VIEWS (TO BE DELETED IN FINAL CLEANUP)
# ═══════════════════════════════════════════════════════════════

# Create your views here.

def logout_view(request):
    logout(request)
    messages.success(request, 'logout successfull !!')
    return redirect('home')


# admin dashboard and functionalities

@login_required   
def admin_dashboard(request):
    users = User.objects.all()
    students = users.filter(groups__name='Students').distinct()
    teachers = users.filter(groups__name='Teachers').distinct()
    parents = users.filter(groups__name='Parents').distinct()
    ungrouped = users.filter(groups__isnull=True).distinct()

    # Applicant stats
    applicants = Applicant.objects.all()
    applicants_pending = applicants.filter(status='pending').count()
    applicants_reviewed = applicants.filter(status='reviewed').count()
    applicants_accepted = applicants.filter(status='accepted').count()
    applicants_rejected = applicants.filter(status='rejected').count()

    return render(request, 'accounts/admin_dashboard.html', {
        'users': users,
        'students': students,
        'teachers': teachers,
        'parents': parents,
        'ungrouped': ungrouped,
        'applicants': applicants,
        'applicants_pending': applicants_pending,
        'applicants_reviewed': applicants_reviewed,
        'applicants_accepted': applicants_accepted,
        'applicants_rejected': applicants_rejected,
    })





@login_required
def aplicant_list(request):
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to view applicants.')
        return redirect('dashboard')

    applicants = Applicant.objects.all()
    return render(request, 'accounts/partials/applicant_list.html', {'applicants': applicants})


@login_required
def delete_applicant(request, pk):
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to delete applicants.')
        return redirect('applicant_list')

    if request.method != 'POST':
        return redirect('applicant_list')

    applicant = get_object_or_404(Applicant, pk=pk)
    applicant.delete()
    messages.success(request, f'Applicant {applicant.first_name} {applicant.last_name} has been deleted.')
    return redirect('applicant_list')


@login_required
def applicant_detail(request, pk):
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to view applicant details.')
        return redirect('dashboard')

    applicant = get_object_or_404(Applicant, pk=pk)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in dict(Applicant.STATUS_CHOICES):
            applicant.status = status
            applicant.save()
            messages.success(request, f'Applicant status updated to {status}.')
    
    return render(request, 'accounts/applicant_detail.html', {'applicant': applicant})


