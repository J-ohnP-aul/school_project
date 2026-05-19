from django.contrib import admin
from .models import SchoolInfo, Staff, Facility, GalleryImage


@admin.register(SchoolInfo)
class SchoolInfoAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name', 'mission', 'vision', 'history']


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['name', 'position']
    search_fields = ['name', 'position']


@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title', 'description']


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ['title', 'uploaded_at']
    search_fields = ['title', 'description']
    readonly_fields = ['uploaded_at']
    ordering = ['-uploaded_at']