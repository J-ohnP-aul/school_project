from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q

from .forms import LoginForm, RegisterForm, StudentProfileForm, TeacherProfileForm, ParentProfileForm
from .forms import AdminCreateUserForm
from .models import StudentProfile, TeacherProfile, ParentProfile
from admissions.models import Applicant
from django.contrib.auth.models import User, Group

ROLE_TO_GROUP = {
    'student': 'Students',
    'teacher': 'Teachers',
    'parent': 'Parents',
}


def get_user_role(user):
    if user.groups.filter(name='Students').exists():
        return 'student'
    if user.groups.filter(name='Teachers').exists():
        return 'teacher'
    if user.groups.filter(name='Parents').exists():
        return 'parent'
    return None


def has_complete_profile(user):
    role = get_user_role(user)
    if role == 'student':
        return StudentProfile.objects.filter(user=user).exists()
    if role == 'teacher':
        return TeacherProfile.objects.filter(user=user).exists()
    if role == 'parent':
        return ParentProfile.objects.filter(user=user).exists()
    return True

# Create your views here.
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            # assign user to group based on selected role
            role = form.cleaned_data.get('role')
            group_map = {
                'student': 'Students',
                'teacher': 'Teachers',
                'parent': 'Parents',
            }
            group_name = group_map.get(role)
            if group_name:
                group, _ = Group.objects.get_or_create(name=group_name)
                user.groups.add(group)

            login(request, user)
            messages.success(request, 'Registration successful. Please complete your profile.')
            return redirect('complete_profile', role=role)
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            selected_role = form.cleaned_data['role']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                allowed = user.is_superuser or user.is_staff
                if not allowed:
                    expected_group = ROLE_TO_GROUP.get(selected_role)
                    allowed = user.groups.filter(name=expected_group).exists()
                if not allowed:
                    messages.error(request, 'You are not authorized to login as that role.')
                else:
                    login(request, user)
                    if not has_complete_profile(user):
                        role = get_user_role(user) or selected_role
                        messages.info(request, 'Please complete your profile before continuing.')
                        return redirect('complete_profile', role=role)
                    messages.success(request, 'Login successful.')
                    return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

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
    if not has_complete_profile(user):
        role = get_user_role(user)
        messages.info(request, 'Please complete your profile before continuing.')
        return redirect('complete_profile', role=role)
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
def create_user(request):
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to create users.')
        return redirect('admin_dashboard')

    if request.method == 'POST':
        form = AdminCreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = form.cleaned_data.get('role')
            group_map = {
                'student': 'Students',
                'teacher': 'Teachers',
                'parent': 'Parents',
            }
            group_name = group_map.get(role)
            if group_name:
                group, _ = Group.objects.get_or_create(name=group_name)
                user.groups.add(group)
            messages.success(request, f'User {user.username} created successfully. The user will complete their profile on first login.')
            return redirect('users_list')
    else:
        form = AdminCreateUserForm()

    return render(request, 'accounts/create_user.html', {'form': form})

@login_required
def users_list(request):
    users = User.objects.all()
    students = users.filter(groups__name='Students').distinct()
    teachers = users.filter(groups__name='Teachers').distinct()
    parents = users.filter(groups__name='Parents').distinct()
    return render(request, 'accounts/partials/users_list.html', {
        'users': users,
        'students': students,
        'teachers': teachers,
        'parents': parents,
    })

@login_required
def delete_user(request, pk):
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to delete users.')
        return redirect('admin_dashboard')

    if request.method != 'POST':
        return redirect('users_list')

    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('users_list')

    user.delete()
    messages.success(request, f'User {user.username} has been deleted.')
    return redirect('users_list')

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


@login_required
def search_students(request):
    q = request.GET.get('q', '').strip()
    results = []
    if q:
        students = StudentProfile.objects.filter(
            Q(user__username__icontains=q) | Q(admission_number__icontains=q)
        ).select_related('user')[:15]
        for s in students:
            results.append({
                'id': s.id,
                'text': f"{s.user.username} — {s.admission_number}" if s.admission_number else s.user.username
            })
    return JsonResponse({'results': results})


@login_required
def complete_profile(request, role):
    role = role.lower()

    form_class_map = {
        'student': (StudentProfileForm, StudentProfile),
        'teacher': (TeacherProfileForm, TeacherProfile),
        'parent': (ParentProfileForm, ParentProfile),
    }

    if role not in form_class_map:
        messages.error(request, 'Invalid profile type.')
        return redirect('dashboard')

    form_class, profile_model = form_class_map[role]

    existing = profile_model.objects.filter(user=request.user).first()
    if existing:
        if role == 'parent' and not existing.students.exists():
            # allow parents who have not linked any students yet to complete the student relation
            form = form_class(request.POST or None, request.FILES or None, instance=existing)
        else:
            messages.info(request, 'Your profile is already completed.')
            return redirect('dashboard')
    else:
        form = form_class(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            if role == 'parent':
                form.save_m2m()
                if not profile.students.exists():
                    messages.warning(request, 'No students linked to your profile. You can add them later from your dashboard.')
            messages.success(request, 'Profile completed.')
            return redirect('dashboard')

    return render(request, 'accounts/complete_profile.html', {'form': form, 'role': role})