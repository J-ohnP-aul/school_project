from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required, user_passes_test

from accounts.models import TeacherProfile, StudentProfile, ParentProfile
from .forms import AssignmentForm, GradeForm, AttendanceForm
from .models import Assignment, Grade, Attendance
from django.db.models import Q
from django.core.paginator import Paginator

def teacher_check(user):

    return user.groups.filter(
        name='Teachers'
    ).exists()

@login_required
@user_passes_test(teacher_check)
def create_assignment(request):
    teacher = TeacherProfile.objects.get(
        user=request.user
    )
    if request.method == 'POST':

        form = AssignmentForm(request.POST)

        if form.is_valid():

            assignment = form.save(commit=False)

            assignment.teacher = teacher

            assignment.save()

            return redirect('assignment_list')
    else:
        form = AssignmentForm()
    return render(
        request,
        'academics/create_assignment.html',
        {
            'form': form
        }
    )
    
@login_required
def assignment_list(request):

    query = request.GET.get('q')

    assignments = Assignment.objects.order_by(
        '-created_at'
    )

    if query:

        assignments = assignments.filter(

            Q(title__icontains=query) |

            Q(description__icontains=query)

        )
        
    paginator = Paginator(assignments, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        'academics/assignment_list.html',
        {
            'page_obj': page_obj,
        }
    )

@login_required
@user_passes_test(teacher_check)
def record_grade(request):

    if request.method == 'POST':

        form = GradeForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect('assignment_list')

    else:

        form = GradeForm()

    return render(
        request,
        'academics/record_grade.html',
        {
            'form': form
        }
    )
    
@login_required
@user_passes_test(teacher_check)
def record_attendance(request):

    teacher = TeacherProfile.objects.get(
        user=request.user
    )

    if request.method == 'POST':

        form = AttendanceForm(request.POST)

        if form.is_valid():

            attendance = form.save(commit=False)

            attendance.recorded_by = teacher

            attendance.save()

            return redirect('assignment_list')

    else:

        form = AttendanceForm()

    return render(
        request,
        'academics/record_attendance.html',
        {
            'form': form
        }
    )

@login_required
def student_dashboard(request):

    student = StudentProfile.objects.get(
        user=request.user
    )

    grades = Grade.objects.filter(
        student=student
    )

    attendance = Attendance.objects.filter(
        student=student
    ).order_by('-date')

    assignments = Assignment.objects.order_by(
        '-created_at'
    )[:5]

    context = {

        'student': student,

        'grades': grades,

        'attendance': attendance,

        'assignments': assignments,
    }

    return render(
        request,
        'academics/student_dashboard.html',
        context
    )

@login_required
def parent_dashboard(request):

    parent = ParentProfile.objects.get(
        user=request.user
    )

    students = parent.students.all()

    return render(
        request,
        'academics/parent_dashboard.html',
        {
            'students': students
        }
    )