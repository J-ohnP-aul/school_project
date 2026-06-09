from django.contrib import admin
from .models import SchoolInfo, Staff, Facility, GalleryImage
# Register your models here.

admin.site.register(SchoolInfo)
admin.site.register(Staff)
admin.site.register(Facility)

@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ['title', 'uploaded_at']
    search_fields = ['title']