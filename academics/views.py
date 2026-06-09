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
from django.utils import timezone

from accounts.models import TeacherProfile, StudentProfile, ParentProfile
from .forms import AssignmentForm, GradeForm, AttendanceForm, AssessmentForm
from .models import (
    Assignment,
    Grade,
    Attendance,
    FeeStructure,
    AcademicProgram,
    Requirement,
    DraftAssessment,
    Assessment,
    Term,
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

# @login_required #legacy
# def student_dashboard(request):
#     # ensure student profile exists; if not, prompt user to complete profile
#     student = StudentProfile.objects.filter(user=request.user).first()

#     if student is None:
#         messages.error(
#             request,
#             'No student profile found for your account. Please complete your student profile before accessing the student dashboard.'
#         )
#         return redirect('dashboard')

#     grades = Grade.objects.filter(
#         student=student
#     )

#     attendance = Attendance.objects.filter(
#         student=student
#     ).order_by('-date')

#     assignments = Assignment.objects.order_by(
#         '-created_at'
#     )[:5]
#     average_score = grades.aggregate(Avg('score'))['score__avg']

#     context = {

#         'student': student,

#         'grades': grades,

#         'attendance': attendance,

#         'assignments': assignments,
#         'average_score': average_score,
#     }

#     return render(
#         request,
#         'academics/student_dashboard.html',
#         context
#     )

# academics/views.py - Updated student_dashboard

@login_required
def student_dashboard(request):
    student = StudentProfile.objects.filter(user=request.user).first()

    if student is None:
        messages.error(request, 'No student profile found.')
        return redirect('dashboard')

    # Get CBC assessments
    assessments = Assessment.objects.filter(student=student).select_related('subject', 'competency', 'term')
    
    # Debug: Print to console
    print(f"Found {assessments.count()} assessments for student {student.user.username}")
    for a in assessments:
        print(f"  - Subject: {a.subject.name}, Term: {a.term.name if a.term else 'NO TERM'}")
    
    # Get ALL terms from database (don't hardcode names)
    all_terms = Term.objects.all().order_by('id')
    
    # Create a dictionary of assessments by term
    assessments_by_term = {}
    for term in all_terms:
        assessments_by_term[term] = assessments.filter(term=term)
    
    # For template compatibility, also create separate variables
    terms_list = list(all_terms)
    assessments_term1 = assessments_by_term.get(terms_list[0], []) if len(terms_list) > 0 else []
    assessments_term2 = assessments_by_term.get(terms_list[1], []) if len(terms_list) > 1 else []
    assessments_term3 = assessments_by_term.get(terms_list[2], []) if len(terms_list) > 2 else []
    
    # Calculate best performance band
    best_band = None
    band_order = ['EE1', 'EE2', 'ME1', 'ME2', 'AE1', 'AE2', 'BE1', 'BE2']
    for band in band_order:
        if assessments.filter(perfomance_band=band).exists():
            best_band = band
            break
    
    # Attendance calculations
    attendance_records = Attendance.objects.filter(student=student).order_by('-date')
    total_attendance = attendance_records.count()
    present_count = attendance_records.filter(status='Present').count()
    attendance_percentage = round((present_count / total_attendance) * 100, 1) if total_attendance > 0 else 0
    
    context = {
        'student': student,
        'assessments_term1': assessments_term1,
        'assessments_term2': assessments_term2,
        'assessments_term3': assessments_term3,
        'all_terms': all_terms,
        'assessments_by_term': assessments_by_term,
        'attendance': attendance_records,
        'total_assessments': assessments.count(),
        'best_band': best_band,
        'attendance_percentage': attendance_percentage,
    }

    return render(request, 'academics/student_dashboard.html', context)
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

# @login_required #legacy
# def parent_report_card(request, student_id):
#     parent = ParentProfile.objects.filter(user=request.user).first()

#     if parent is None:
#         messages.error(
#             request,
#             'No parent profile found for your account. Please create one or ask an admin to link your user.'
#         )
#         return redirect('dashboard')

#     student = get_object_or_404(StudentProfile, pk=student_id)

#     if student not in parent.students.all():
#         messages.error(request, 'You are not authorized to view this student report card.')
#         return redirect('academics:parent_dashboard')

#     grades = Grade.objects.filter(student=student).select_related('assignment__teacher')
#     average_score = grades.aggregate(Avg('score'))['score__avg'] or 0

#     attendance = Attendance.objects.filter(student=student)
#     total_attendance = attendance.count()
#     attendance_percentage = round((attendance.filter(status='Present').count() / total_attendance) * 100, 1) if total_attendance else 0

#     report_context = {
#         'student': student,
#         'grades': grades,
#         'average_score': round(average_score, 1) if average_score else 0,
#         'attendance_percentage': attendance_percentage,
#         'total_attendance': total_attendance,
#         'present_days': attendance.filter(status='Present').count(),
#         'absent_days': attendance.filter(status='Absent').count(),
#     }

#     buffer = BytesIO()
#     pdf = canvas.Canvas(buffer, pagesize=letter)
#     width, height = letter
#     margin = 40
#     y = height - margin

#     pdf.setFont('Helvetica-Bold', 18)
#     pdf.drawString(margin, y, 'Student Report Card')
#     y -= 24

#     student_name = student.user.get_full_name() or student.user.username
#     pdf.setFont('Helvetica', 10)
#     pdf.drawString(margin, y, f'Student: {student_name}')
#     pdf.drawString(width - margin - 200, y, f'Date: {datetime.datetime.now().strftime("%B %d, %Y")}')
#     y -= 14
#     pdf.drawString(margin, y, f'Admission Number: {student.admission_number}')
#     y -= 14
#     pdf.drawString(margin, y, f'Grade Level: {student.grade}')
#     y -= 14
#     pdf.drawString(margin, y, f'Average Score: {report_context["average_score"]}')
#     y -= 14
#     pdf.drawString(margin, y, f'Attendance: {attendance_percentage}% ({report_context["present_days"]} present, {report_context["absent_days"]} absent)')
#     y -= 24

#     pdf.setFont('Helvetica-Bold', 12)
#     pdf.drawString(margin, y, 'Assignment Results')
#     y -= 18

#     pdf.setFont('Helvetica-Bold', 10)
#     pdf.drawString(margin, y, 'Assignment')
#     pdf.drawString(margin + 180, y, 'Teacher')
#     pdf.drawString(margin + 320, y, 'Score')
#     pdf.drawString(margin + 370, y, 'Remarks')
#     pdf.drawString(margin + 490, y, 'Due')
#     y -= 12
#     pdf.line(margin, y, width - margin, y)
#     y -= 14

#     pdf.setFont('Helvetica', 10)
#     if not grades.exists():
#         pdf.drawString(margin, y, 'No grades recorded yet for this student.')
#         y -= 14
#     else:
#         for grade in grades:
#             assignment_title = grade.assignment.title[:28]
#             teacher_name = grade.assignment.teacher.user.get_full_name() or grade.assignment.teacher.user.username
#             teacher_name = teacher_name[:20]
#             remarks = (grade.remarks or 'N/A').replace('\n', ' ')[:20]
#             due_date = grade.assignment.due_date.strftime('%Y-%m-%d')

#             if y < margin + 80:
#                 pdf.showPage()
#                 y = height - margin
#                 pdf.setFont('Helvetica-Bold', 12)
#                 pdf.drawString(margin, y, 'Student Report Card (continued)')
#                 y -= 24
#                 pdf.setFont('Helvetica-Bold', 10)
#                 pdf.drawString(margin, y, 'Assignment')
#                 pdf.drawString(margin + 180, y, 'Teacher')
#                 pdf.drawString(margin + 320, y, 'Score')
#                 pdf.drawString(margin + 370, y, 'Remarks')
#                 pdf.drawString(margin + 490, y, 'Due')
#                 y -= 12
#                 pdf.line(margin, y, width - margin, y)
#                 y -= 14
#                 pdf.setFont('Helvetica', 10)

#             pdf.drawString(margin, y, assignment_title)
#             pdf.drawString(margin + 180, y, teacher_name)
#             pdf.drawString(margin + 320, y, str(grade.score))
#             pdf.drawString(margin + 370, y, remarks)
#             pdf.drawString(margin + 490, y, due_date)
#             y -= 14

#     pdf.showPage()
#     pdf.save()
#     buffer.seek(0)

#     response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
#     response['Content-Disposition'] = f'attachment; filename="report-card-{student.user.username}.pdf"'
#     return response
# academics/views.py - Updated parent_report_card for CBC

@login_required
def parent_report_card(request, student_id):
    parent = ParentProfile.objects.filter(user=request.user).first()

    if parent is None:
        messages.error(request, 'No parent profile found.')
        return redirect('dashboard')

    student = get_object_or_404(StudentProfile, pk=student_id)

    if student not in parent.students.all():
        messages.error(request, 'You are not authorized to view this student report card.')
        return redirect('academics:parent_dashboard')

    # Get CBC assessments instead of grades
    assessments = Assessment.objects.filter(student=student).select_related('subject', 'competency', 'term', 'teacher')
    
    # Group assessments by term
    terms = Term.objects.all()
    assessments_by_term = {}
    for term in terms:
        assessments_by_term[term] = assessments.filter(term=term)
    
    # Get attendance
    attendance = Attendance.objects.filter(student=student)
    total_attendance = attendance.count()
    attendance_percentage = round((attendance.filter(status='Present').count() / total_attendance) * 100, 1) if total_attendance else 0
    
    # Performance summary
    total_assessments = assessments.count()
    
    # Count assessments by band
    band_counts = {
        'EE1': assessments.filter(perfomance_band='EE1').count(),
        'EE2': assessments.filter(perfomance_band='EE2').count(),
        'ME1': assessments.filter(perfomance_band='ME1').count(),
        'ME2': assessments.filter(perfomance_band='ME2').count(),
        'AE1': assessments.filter(perfomance_band='AE1').count(),
        'AE2': assessments.filter(perfomance_band='AE2').count(),
        'BE1': assessments.filter(perfomance_band='BE1').count(),
        'BE2': assessments.filter(perfomance_band='BE2').count(),
    }
    
    report_context = {
        'student': student,
        'assessments_by_term': assessments_by_term,
        'terms': terms,
        'attendance_percentage': attendance_percentage,
        'total_attendance': total_attendance,
        'present_days': attendance.filter(status='Present').count(),
        'absent_days': attendance.filter(status='Absent').count(),
        'total_assessments': total_assessments,
        'band_counts': band_counts,
        'generated_date': datetime.datetime.now(),
    }

    # Generate PDF
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    margin = 40
    y = height - margin

    # Header
    pdf.setFont('Helvetica-Bold', 18)
    pdf.drawString(margin, y, 'CBC PROGRESS REPORT CARD')
    y -= 24

    pdf.setFont('Helvetica-Bold', 12)
    pdf.drawString(margin, y, 'Competency-Based Curriculum (CBC)')
    y -= 20
    
    pdf.setFont('Helvetica', 10)
    pdf.drawString(margin, y, f'Student: {student.user.get_full_name() or student.user.username}')
    pdf.drawString(width - margin - 150, y, f'Date: {datetime.datetime.now().strftime("%B %d, %Y")}')
    y -= 14
    pdf.drawString(margin, y, f'Admission Number: {student.admission_number}')
    y -= 14
    pdf.drawString(margin, y, f'Grade: {student.grade}')
    if student.stream:
        pdf.drawString(margin + 200, y, f'Stream: {student.stream}')
    y -= 14
    pdf.drawString(margin, y, f'Attendance: {attendance_percentage}% ({report_context["present_days"]} present, {report_context["absent_days"]} absent)')
    y -= 24

    # Important CBC Note
    pdf.setFont('Helvetica-Oblique', 9)
    pdf.setFillColorRGB(0.5, 0.5, 0.5)
    pdf.drawString(margin, y, 'Note: Under CBC, no aggregate score is calculated. Performance is reported per learning area.')
    pdf.setFillColorRGB(0, 0, 0)
    y -= 20

    # Performance Band Guide
    pdf.setFont('Helvetica-Bold', 10)
    pdf.drawString(margin, y, 'Performance Band Guide:')
    y -= 14
    
    pdf.setFont('Helvetica', 8)
    band_guide = [
        'EE1: Exceeding Expectations (90-100%) - 8 points',
        'EE2: Exceeding Expectations (75-89%) - 7 points',
        'ME1: Meeting Expectations (58-74%) - 6 points',
        'ME2: Meeting Expectations (41-57%) - 5 points',
        'AE1: Approaching Expectations (31-40%) - 4 points',
        'AE2: Approaching Expectations (21-30%) - 3 points',
        'BE1: Below Expectations (11-20%) - 2 points',
        'BE2: Below Expectations (1-10%) - 1 point',
    ]
    
    for guide in band_guide:
        pdf.drawString(margin + 20, y, f'• {guide}')
        y -= 10
        if y < margin + 100:
            pdf.showPage()
            y = height - margin
            pdf.setFont('Helvetica', 8)
    
    y -= 10

    # Assessment Results by Term
    for term in terms:
        term_assessments = assessments_by_term.get(term, [])
        if term_assessments.exists():
            # Check if we need a new page
            if y < margin + 80:
                pdf.showPage()
                y = height - margin
                pdf.setFont('Helvetica-Bold', 12)
                pdf.drawString(margin, y, f'{term.name} - Continued')
                y -= 20
            
            pdf.setFont('Helvetica-Bold', 12)
            pdf.drawString(margin, y, f'{term.name} Results')
            y -= 18
            
            # Table headers
            pdf.setFont('Helvetica-Bold', 9)
            pdf.drawString(margin, y, 'Learning Area')
            pdf.drawString(margin + 100, y, 'Competency')
            pdf.drawString(margin + 220, y, 'Band')
            pdf.drawString(margin + 280, y, 'Points')
            pdf.drawString(margin + 340, y, 'Remarks')
            y -= 10
            pdf.line(margin, y, width - margin, y)
            y -= 14
            
            pdf.setFont('Helvetica', 9)
            for assessment in term_assessments:
                if y < margin + 60:
                    pdf.showPage()
                    y = height - margin
                    pdf.setFont('Helvetica-Bold', 12)
                    pdf.drawString(margin, y, f'{term.name} Results (continued)')
                    y -= 20
                    pdf.setFont('Helvetica-Bold', 9)
                    pdf.drawString(margin, y, 'Learning Area')
                    pdf.drawString(margin + 100, y, 'Competency')
                    pdf.drawString(margin + 220, y, 'Band')
                    pdf.drawString(margin + 280, y, 'Points')
                    pdf.drawString(margin + 340, y, 'Remarks')
                    y -= 10
                    pdf.line(margin, y, width - margin, y)
                    y -= 14
                    pdf.setFont('Helvetica', 9)
                
                # Truncate long text
                subject_name = (assessment.subject.name[:25] if assessment.subject.name else 'N/A')
                competency_name = (assessment.competency.name[:20] if assessment.competency else 'General')
                remarks = (assessment.remarks[:30] if assessment.remarks else '-')
                
                # Get points for band
                points_map = {'EE1': 8, 'EE2': 7, 'ME1': 6, 'ME2': 5, 'AE1': 4, 'AE2': 3, 'BE1': 2, 'BE2': 1}
                points = points_map.get(assessment.perfomance_band, 0)
                
                pdf.drawString(margin, y, subject_name)
                pdf.drawString(margin + 100, y, competency_name)
                pdf.drawString(margin + 220, y, assessment.perfomance_band)
                pdf.drawString(margin + 280, y, str(points))
                pdf.drawString(margin + 340, y, remarks)
                y -= 14
            
            y -= 10

    # Summary Section (No aggregate!)
    if y < margin + 80:
        pdf.showPage()
        y = height - margin
    
    pdf.setFont('Helvetica-Bold', 12)
    pdf.drawString(margin, y, 'Performance Summary')
    y -= 18
    
    pdf.setFont('Helvetica', 10)
    pdf.drawString(margin, y, f'Total Assessments: {total_assessments}')
    y -= 14
    
    # Band distribution
    pdf.drawString(margin, y, 'Performance Band Distribution:')
    y -= 14
    
    pdf.setFont('Helvetica', 9)
    for band, count in band_counts.items():
        if count > 0:
            band_label = {
                'EE1': 'EE1 (90-100%)', 'EE2': 'EE2 (75-89%)',
                'ME1': 'ME1 (58-74%)', 'ME2': 'ME2 (41-57%)',
                'AE1': 'AE1 (31-40%)', 'AE2': 'AE2 (21-30%)',
                'BE1': 'BE1 (11-20%)', 'BE2': 'BE2 (1-10%)'
            }.get(band, band)
            pdf.drawString(margin + 20, y, f'• {band_label}: {count} assessment(s)')
            y -= 12
    
    y -= 10
    
    # Teacher comments section
    pdf.setFont('Helvetica-Bold', 10)
    pdf.drawString(margin, y, 'Teacher Comments:')
    y -= 14
    pdf.setFont('Helvetica-Oblique', 9)
    pdf.drawString(margin + 10, y, '___________________________________________________________________')
    y -= 12
    pdf.drawString(margin + 10, y, '___________________________________________________________________')
    y -= 12
    pdf.drawString(margin + 10, y, '___________________________________________________________________')

    pdf.save()
    buffer.seek(0)

    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="cbc-report-{student.user.username}.pdf"'
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

    # NEW: Get pending drafts count
    pending_drafts_count = DraftAssessment.objects.filter(teacher=teacher).count()
    
    # Get recent drafts (last 3) for display
    recent_drafts = DraftAssessment.objects.filter(teacher=teacher).select_related('subject', 'competency', 'term')[:3]

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
        # NEW: Add these to context
        'pending_drafts_count': pending_drafts_count,
        'recent_drafts': recent_drafts,
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
# academics/views.py

from django.http import JsonResponse
from django.core.paginator import Paginator
from django.contrib import messages
from django.views.decorators.http import require_http_methods
import json

from .models import Subject, Competency, Term, Assessment, DraftAssessment
from accounts.models import StudentProfile, TeacherProfile

@login_required
def record_assessment(request):
    # Get the teacher profile
    try:
        teacher = TeacherProfile.objects.get(user=request.user)
    except TeacherProfile.DoesNotExist:
        messages.error(request, "Teacher profile not found.")
        return redirect('dashboard')
    
    # Get all filter data for dropdowns
    subjects = Subject.objects.all().order_by('name')
    competencies = Competency.objects.all().order_by('name')
    terms = Term.objects.all().order_by('id')
    
    # Get unique grades from StudentProfile
    grades = StudentProfile.objects.values_list('grade', flat=True).distinct().order_by('grade')
    
    # NEW: Check if loading a specific draft
    draft_id = request.GET.get('draft')
    draft_data = None
    if draft_id:
        try:
            draft = DraftAssessment.objects.get(id=draft_id, teacher=teacher)
            draft_data = {
                'id': draft.id,
                'grade': draft.grade,
                'stream': draft.stream,
                'subject_id': draft.subject_id,
                'competency_id': draft.competency_id,
                'term_id': draft.term_id,
                'data': draft.draft_data
            }
        except DraftAssessment.DoesNotExist:
            pass
    
    context = {
        'subjects': subjects,
        'competencies': competencies,
        'terms': terms,
        'grades': grades,
        'draft_data': draft_data,  # NEW
    }
    
    return render(request, 'academics/record_assessment_table.html', context)

@login_required
def get_streams(request):
    """AJAX endpoint to get streams for a selected grade"""
    grade = request.GET.get('grade')
    
    if grade:
        streams = StudentProfile.objects.filter(grade=grade)\
            .exclude(stream='')\
            .values_list('stream', flat=True)\
            .distinct()\
            .order_by('stream')
        
        stream_list = [{'value': s, 'label': s} for s in streams]
        
        # Add option for "All Streams"
        stream_list.insert(0, {'value': '', 'label': '-- All Streams --'})
        
        return JsonResponse({'streams': stream_list})
    
    return JsonResponse({'streams': []})


@login_required
def get_students(request):
    """AJAX endpoint to get students based on grade and stream"""
    grade = request.GET.get('grade')
    stream = request.GET.get('stream', '')
    subject_id = request.GET.get('subject')
    competency_id = request.GET.get('competency')
    term_id = request.GET.get('term')
    page = request.GET.get('page', 1)
    
    if not all([grade, subject_id, competency_id, term_id]):
        return JsonResponse({'error': 'Missing required fields'}, status=400)
    
    # Filter students
    students = StudentProfile.objects.filter(grade=grade)
    
    if stream:
        students = students.filter(stream=stream)
    
    # Order by name
    students = students.order_by('user__first_name', 'user__last_name')
    
    # Pagination (20 per page)
    paginator = Paginator(students, 20)
    students_page = paginator.get_page(page)
    
    # Check for existing draft
    draft = None
    teacher = TeacherProfile.objects.get(user=request.user)
    
    try:
        draft = DraftAssessment.objects.filter(
            teacher=teacher,
            grade=grade,
            stream=stream,
            subject_id=subject_id,
            competency_id=competency_id,
            term_id=term_id
        ).first()
    except DraftAssessment.DoesNotExist:
        pass
    
    # Prepare student data
    student_data = []
    for student in students_page:
        student_info = {
            'id': student.id,
            'name': student.user.get_full_name() or student.user.username,
            'admission_number': student.admission_number,
            'percentage': '',
            'remarks': '',
            'absent': False,
        }
        
        # Load draft data if exists
        if draft and draft.draft_data:
            draft_info = draft.draft_data.get(str(student.id), {})
            student_info['percentage'] = draft_info.get('percentage', '')
            student_info['remarks'] = draft_info.get('remarks', '')
            student_info['absent'] = draft_info.get('absent', False)
        
        student_data.append(student_info)
    
    return JsonResponse({
        'students': student_data,
        'has_previous': students_page.has_previous(),
        'has_next': students_page.has_next(),
        'previous_page_number': students_page.previous_page_number() if students_page.has_previous() else None,
        'next_page_number': students_page.next_page_number() if students_page.has_next() else None,
        'current_page': students_page.number,
        'total_pages': paginator.num_pages,
        'total_students': paginator.count,
        'draft_id': draft.id if draft else None,
    })


@login_required
@require_http_methods(['POST'])
def save_draft(request):
    """Save draft assessment"""
    try:
        teacher = TeacherProfile.objects.get(user=request.user)
        data = json.loads(request.body)
        
        # Get or create draft
        draft, created = DraftAssessment.objects.update_or_create(
            teacher=teacher,
            grade=data.get('grade'),
            stream=data.get('stream', ''),
            subject_id=data.get('subject_id'),
            competency_id=data.get('competency_id'),
            term_id=data.get('term_id'),
            defaults={
                'draft_data': data.get('draft_data', {}),
                'updated_at': timezone.now()
            }
        )
        
        return JsonResponse({
            'success': True,
            'draft_id': draft.id,
            'message': 'Draft saved successfully!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@require_http_methods(['POST'])
def submit_assessments(request):
    """Submit final assessments"""
    try:
        teacher = TeacherProfile.objects.get(user=request.user)
        data = json.loads(request.body)
        
        grade = data.get('grade')
        stream = data.get('stream', '')
        subject_id = data.get('subject_id')
        competency_id = data.get('competency_id')
        term_id = data.get('term_id')
        assessments_data = data.get('assessments', {})
        
        saved_count = 0
        skipped_count = 0
        
        for student_id_str, assessment_info in assessments_data.items():
            student_id = int(student_id_str)
            
            # Skip if absent
            if assessment_info.get('absent', False):
                skipped_count += 1
                continue
            
            percentage = assessment_info.get('percentage')
            
            # Skip if no percentage
            if not percentage:
                skipped_count += 1
                continue
            
            # Calculate performance band from percentage
            percentage_float = float(percentage)
            performance_band = get_band_from_percentage(percentage_float)
            
            # Create or update assessment
            Assessment.objects.update_or_create(
                student_id=student_id,
                teacher=teacher,
                subject_id=subject_id,
                competency_id=competency_id,
                term_id=term_id,
                defaults={
                    'perfomance_band': performance_band,
                    'remarks': assessment_info.get('remarks', ''),
                }
            )
            saved_count += 1
        
        # Delete draft if exists
        DraftAssessment.objects.filter(
            teacher=teacher,
            grade=grade,
            stream=stream,
            subject_id=subject_id,
            competency_id=competency_id,
            term_id=term_id
        ).delete()
        
        return JsonResponse({
            'success': True,
            'saved': saved_count,
            'skipped': skipped_count,
            'message': f'Successfully saved {saved_count} assessments. Skipped {skipped_count} students.'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


def get_band_from_percentage(percentage):
    """Helper function to determine performance band from percentage"""
    if percentage >= 90:
        return 'EE1'
    elif percentage >= 75:
        return 'EE2'
    elif percentage >= 58:
        return 'ME1'
    elif percentage >= 41:
        return 'ME2'
    elif percentage >= 31:
        return 'AE1'
    elif percentage >= 21:
        return 'AE2'
    elif percentage >= 11:
        return 'BE1'
    else:
        return 'BE2'


@login_required
def pending_drafts(request):
    """View to show teacher's pending drafts"""
    try:
        teacher = TeacherProfile.objects.get(user=request.user)
        drafts = DraftAssessment.objects.filter(teacher=teacher).select_related('subject', 'competency', 'term')
        
        # Calculate completion for each draft
        for draft in drafts:
            total_students = StudentProfile.objects.filter(
                grade=draft.grade
            )
            if draft.stream:
                total_students = total_students.filter(stream=draft.stream)
            
            total_count = total_students.count()
            filled_count = len([s for s in draft.draft_data.values() if s.get('percentage')])
            
            draft.completion = f"{filled_count}/{total_count}"
        
        return render(request, 'academics/pending_drafts.html', {'drafts': drafts})
        
    except TeacherProfile.DoesNotExist:
        messages.error(request, "Teacher profile not found.")
        return redirect('dashboard')


@login_required
@require_http_methods(['POST'])
def delete_draft(request, draft_id):
    """Delete a draft"""
    try:
        teacher = TeacherProfile.objects.get(user=request.user)
        draft = get_object_or_404(DraftAssessment, id=draft_id, teacher=teacher)
        draft.delete()
        
        messages.success(request, "Draft deleted successfully.")
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)