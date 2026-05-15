from django.urls import path

from .views import create_assignment, assignment_list, record_grade, record_attendance, student_dashboard, parent_dashboard

app_name = 'academics'

urlpatterns = [
    path('', assignment_list, name='assignment_list' ),
    path('create/',create_assignment,name='create_assignment'),
    path('record-grade/', record_grade, name='record_grade'),
    path('record-attendance/', record_attendance, name='record_attendance'),
    path('student-dashboard/', student_dashboard, name='student_dashboard'),
    path('parent-dashboard/', parent_dashboard, name='parent_dashboard'),
]