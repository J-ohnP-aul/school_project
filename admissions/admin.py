from django.contrib import admin
from .models import Applicant


@admin.register(Applicant)
class ApplicantAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'applying_grade', 'status', 'submitted_at']
    list_filter = ['applying_grade', 'status']
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'previous_school']
    readonly_fields = ['submitted_at']
    actions = ['mark_reviewed', 'mark_accepted', 'mark_rejected']

    def mark_reviewed(self, request, queryset):
        queryset.update(status='reviewed')
        self.message_user(request, 'Selected applicants marked as reviewed.')
    mark_reviewed.short_description = 'Mark selected applicants as reviewed'

    def mark_accepted(self, request, queryset):
        queryset.update(status='accepted')
        self.message_user(request, 'Selected applicants marked as accepted.')
    mark_accepted.short_description = 'Mark selected applicants as accepted'

    def mark_rejected(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, 'Selected applicants marked as rejected.')
    mark_rejected.short_description = 'Mark selected applicants as rejected'