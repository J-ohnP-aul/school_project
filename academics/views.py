from io import BytesIO
import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test

from accounts.models import TeacherProfile, StudentProfile, ParentProfile
from .forms import AssignmentForm, GradeForm, AttendanceForm
from .models import (
    Assignment,
    Grade,
    Attendance,
    FeeStructure,
    AcademicProgram,
    Requirement,
)
from django.db.models import Q
from django.core.paginator import Paginator
from django.db.models import Avg

def teacher_check(user):

    return user.groups.filter(
        name='Teachers'
    ).exists()


def parent_check(user):

    return user.groups.filter(
        name='Parents'
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

            return redirect('academics:assignment_list')
    else:
        form = AssignmentForm()
    return render(
        request,
        'academics/create_assignment.html',
        {
            'form': form
        }
    )
    
def assignment_list(request):
    
    if not request.user.is_authenticated:
        return fee_structure(request)

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

            return redirect('academics:teacher_dashboard')

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

            return redirect('academics:teacher_dashboard')

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
    # ensure student profile exists; if not, prompt user to complete profile
    student = StudentProfile.objects.filter(user=request.user).first()

    if student is None:
        messages.error(
            request,
            'No student profile found for your account. Please complete your student profile before accessing the student dashboard.'
        )
        return redirect('dashboard')

    grades = Grade.objects.filter(
        student=student
    )

    attendance = Attendance.objects.filter(
        student=student
    ).order_by('-date')

    assignments = Assignment.objects.order_by(
        '-created_at'
    )[:5]
    average_score = grades.aggregate(Avg('score'))['score__avg']

    context = {

        'student': student,

        'grades': grades,

        'attendance': attendance,

        'assignments': assignments,
        'average_score': average_score,
    }

    return render(
        request,
        'academics/student_dashboard.html',
        context
    )

@login_required
def parent_dashboard(request):

    parent = ParentProfile.objects.filter(
        user=request.user
    ).first()

    if parent is None:
        messages.error(
            request,
            'No parent profile found for your account. Please create one or ask an admin to link your user.'
        )
        return redirect('dashboard')

    students = parent.students.all()

    return render(
        request,
        'academics/parent_dashboard.html',
        {
            'students': students
        }
    )

@login_required
def parent_report_card(request, student_id):
    parent = ParentProfile.objects.filter(user=request.user).first()

    if parent is None:
        messages.error(
            request,
            'No parent profile found for your account. Please create one or ask an admin to link your user.'
        )
        return redirect('dashboard')

    student = get_object_or_404(StudentProfile, pk=student_id)

    if student not in parent.students.all():
        messages.error(request, 'You are not authorized to view this student report card.')
        return redirect('academics:parent_dashboard')

    grades = Grade.objects.filter(student=student).select_related('assignment__teacher')
    average_score = grades.aggregate(Avg('score'))['score__avg'] or 0

    attendance = Attendance.objects.filter(student=student)
    total_attendance = attendance.count()
    attendance_percentage = round((attendance.filter(status='Present').count() / total_attendance) * 100, 1) if total_attendance else 0

    report_context = {
        'student': student,
        'grades': grades,
        'average_score': round(average_score, 1) if average_score else 0,
        'attendance_percentage': attendance_percentage,
        'total_attendance': total_attendance,
        'present_days': attendance.filter(status='Present').count(),
        'absent_days': attendance.filter(status='Absent').count(),
    }

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    margin = 40
    y = height - margin

    pdf.setFont('Helvetica-Bold', 18)
    pdf.drawString(margin, y, 'Student Report Card')
    y -= 24

    student_name = student.user.get_full_name() or student.user.username
    pdf.setFont('Helvetica', 10)
    pdf.drawString(margin, y, f'Student: {student_name}')
    pdf.drawString(width - margin - 200, y, f'Date: {datetime.datetime.now().strftime("%B %d, %Y")}')
    y -= 14
    pdf.drawString(margin, y, f'Admission Number: {student.admission_number}')
    y -= 14
    pdf.drawString(margin, y, f'Grade Level: {student.grade}')
    y -= 14
    pdf.drawString(margin, y, f'Average Score: {report_context["average_score"]}')
    y -= 14
    pdf.drawString(margin, y, f'Attendance: {attendance_percentage}% ({report_context["present_days"]} present, {report_context["absent_days"]} absent)')
    y -= 24

    pdf.setFont('Helvetica-Bold', 12)
    pdf.drawString(margin, y, 'Assignment Results')
    y -= 18

    pdf.setFont('Helvetica-Bold', 10)
    pdf.drawString(margin, y, 'Assignment')
    pdf.drawString(margin + 180, y, 'Teacher')
    pdf.drawString(margin + 320, y, 'Score')
    pdf.drawString(margin + 370, y, 'Remarks')
    pdf.drawString(margin + 490, y, 'Due')
    y -= 12
    pdf.line(margin, y, width - margin, y)
    y -= 14

    pdf.setFont('Helvetica', 10)
    if not grades.exists():
        pdf.drawString(margin, y, 'No grades recorded yet for this student.')
        y -= 14
    else:
        for grade in grades:
            assignment_title = grade.assignment.title[:28]
            teacher_name = grade.assignment.teacher.user.get_full_name() or grade.assignment.teacher.user.username
            teacher_name = teacher_name[:20]
            remarks = (grade.remarks or 'N/A').replace('\n', ' ')[:20]
            due_date = grade.assignment.due_date.strftime('%Y-%m-%d')

            if y < margin + 80:
                pdf.showPage()
                y = height - margin
                pdf.setFont('Helvetica-Bold', 12)
                pdf.drawString(margin, y, 'Student Report Card (continued)')
                y -= 24
                pdf.setFont('Helvetica-Bold', 10)
                pdf.drawString(margin, y, 'Assignment')
                pdf.drawString(margin + 180, y, 'Teacher')
                pdf.drawString(margin + 320, y, 'Score')
                pdf.drawString(margin + 370, y, 'Remarks')
                pdf.drawString(margin + 490, y, 'Due')
                y -= 12
                pdf.line(margin, y, width - margin, y)
                y -= 14
                pdf.setFont('Helvetica', 10)

            pdf.drawString(margin, y, assignment_title)
            pdf.drawString(margin + 180, y, teacher_name)
            pdf.drawString(margin + 320, y, str(grade.score))
            pdf.drawString(margin + 370, y, remarks)
            pdf.drawString(margin + 490, y, due_date)
            y -= 14

    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="report-card-{student.user.username}.pdf"'
    return response

# ── Replace your teacher_dashboard view with this ──────────────────────────

@login_required
@user_passes_test(teacher_check)
def teacher_dashboard(request):
    teacher = TeacherProfile.objects.get(user=request.user)

    # Assignments this teacher created
    assignments = Assignment.objects.filter(
        teacher=teacher
    ).order_by('-created_at')

    # Recent grades recorded on this teacher's assignments
    recent_grades = Grade.objects.filter(
        assignment__teacher=teacher
    ).select_related('student', 'assignment').order_by('-id')[:10]

    # Recent attendance recorded by this teacher
    recent_attendance = Attendance.objects.filter(
        recorded_by=teacher
    ).select_related('student').order_by('-date')[:10]

    # Stats
    total_assignments = assignments.count()

    total_grades = Grade.objects.filter(
        assignment__teacher=teacher
    ).count()

    avg_score = Grade.objects.filter(
        assignment__teacher=teacher
    ).aggregate(Avg('score'))['score__avg']

    present_count = Attendance.objects.filter(
        recorded_by=teacher,
        status='Present'
    ).count()

    total_attendance = Attendance.objects.filter(
        recorded_by=teacher
    ).count()

    attendance_rate = round(
        (present_count / total_attendance * 100), 1
    ) if total_attendance > 0 else 0

    context = {
        'teacher':           teacher,
        'assignments':       assignments[:6],
        'recent_grades':     recent_grades,
        'recent_attendance': recent_attendance,
        'total_assignments': total_assignments,
        'total_grades':      total_grades,
        'avg_score':         round(avg_score, 1) if avg_score else 0,
        'attendance_rate':   attendance_rate,
    }

    return render(request, 'academics/teacher_dashboard.html', context)

def fee_structure(request):
    fee_items = FeeStructure.objects.order_by('year', 'level', 'term')
    fee_by_level = {}
    for item in fee_items:
        fee_by_level.setdefault(item.level, []).append(item)

    context = {
        'fee_by_level': fee_by_level,
        'programs': AcademicProgram.objects.all(),
        'requirements': Requirement.objects.all(),
        'other_charges': getattr(settings, 'ACADEMICS_OTHER_CHARGES', []),
        'bank_details': getattr(settings, 'ACADEMICS_BANK_DETAILS', {}),
    }

    return render(request, 'academics/fee_structure.html', context)
