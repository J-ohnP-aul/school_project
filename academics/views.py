from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect

from django.contrib.auth.decorators import (
    login_required,
    user_passes_test
)

from accounts.models import TeacherProfile
from .forms import AssignmentForm
from .models import Assignment

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
    assignments = Assignment.objects.order_by(
        '-created_at'
    )
    return render(
        request,
        'academics/assignment_list.html',
        {
            'assignments': assignments
        }
    )