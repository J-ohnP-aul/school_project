from django.contrib import admin
from .models import SchoolInfo, Staff, Facility
# Register your models here.

admin.site.register(SchoolInfo)
admin.site.register(Staff)
admin.site.register(Facility)