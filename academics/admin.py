from django.contrib import admin
from .models import Assignment, Grade, Attendance, FeeStructure, AcademicProgram, Requirement, GradeLevel, Term, Subject
# Register your models here.

admin.site.register(Assignment)
admin.site.register(Grade)
admin.site.register(Attendance)
admin.site.register(GradeLevel)
admin.site.register(Term)
admin.site.register(Subject)

@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ('level', 'term', 'year', 'amount')
    list_filter = ('level', 'term', 'year')
    search_fields = ('level',)


@admin.register(AcademicProgram)
class AcademicProgramAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name', 'description')


@admin.register(Requirement)
class RequirementAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
