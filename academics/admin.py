from django.contrib import admin
from .models import Assignment, Grade, Attendance
# Register your models here.

admin.site.register(Assignment)
admin.site.register(Grade)
admin.site.register(Attendance)