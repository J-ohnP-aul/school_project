from django.urls import path

from .views import (
    create_assignment,
    assignment_list,
    record_grade,
    record_attendance,
    student_dashboard,
    parent_dashboard,
    parent_report_card,
    teacher_dashboard,
    fee_structure,
    record_assessment,
    get_streams,
    get_students,
    save_draft,
    submit_assessments,
    pending_drafts,
    delete_draft,
    
)

app_name = 'academics'

urlpatterns = [
    path('parent-dashboard/', parent_dashboard, name='parent_dashboard'),
    path('student-dashboard/', student_dashboard, name='student_dashboard'),
    path('teacher-dashboard/', teacher_dashboard, name='teacher_dashboard'),
    path('parent-dashboard/report/<int:student_id>/', parent_report_card, name='parent_report_card'),

    path('create/',create_assignment,name='create_assignment'),
    path('', assignment_list, name='assignment_list' ),

    path('record-grade/', record_grade, name='record_grade'),
    path('record-attendance/', record_attendance, name='record_attendance'),

    path('fee-structure/', fee_structure, name='fee_structure'),

    path('record-assessment/', record_assessment, name='record_assessment'),  
    path('pending-drafts/', pending_drafts, name='pending_drafts'),
    path('delete-draft/<int:draft_id>/', delete_draft, name='delete_draft'),

    path('api/submit-assessments/', submit_assessments, name='submit_assessments'),
    path('api/get-streams/', get_streams, name='get_streams'),
    path('api/get-students/', get_students, name='get_students'),
    path('api/save-draft/', save_draft, name='save_draft'),
]