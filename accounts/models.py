from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    admission_number = models.CharField(max_length=20, unique=True)
    grade = models.CharField(max_length=50)
    stream = models.CharField(
        max_length=30,
        blank=True
    )
    profile_picture = models.ImageField(upload_to='students/', blank=True, null=True)
    guardian_name = models.CharField(max_length=100)
    guardian_phone = models.CharField(max_length=20)
    stream = models.CharField(max_length=30,blank=True)

    def __str__(self):
        return self.user.username

    @property
    def average_grade(self):
        try:
            from academics.models import Grade
            from django.db.models import Avg
            avg = Grade.objects.filter(student=self).aggregate(Avg('score'))['score__avg']
            return round(avg, 1) if avg is not None else 0
        except Exception:
            return 0

    @property
    def assignments_count(self):
        try:
            from academics.models import Grade
            return Grade.objects.filter(student=self).count()
        except Exception:
            return 0

    @property
    def attendance_percentage(self):
        try:
            from academics.models import Attendance
            total = Attendance.objects.filter(student=self).count()
            if total == 0:
                return 0
            present = Attendance.objects.filter(student=self, status='Present').count()
            return round((present / total) * 100, 1)
        except Exception:
            return 0

    @property
    def recent_activities(self):
        # returns a list of dicts with 'description' keys for the template
        activities = []
        try:
            from academics.models import Grade, Attendance
            grades = Grade.objects.filter(student=self).select_related('assignment').order_by('-id')[:3]
            for g in grades:
                activities.append({'description': f'Grade recorded: {g.assignment.title} — {g.score}'})

            attendance = Attendance.objects.filter(student=self).order_by('-date')[:3]
            for a in attendance:
                activities.append({'description': f'Attendance {a.date}: {a.status}'})

        except Exception:
            pass
        return activities
    
class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    profile_picture = models.ImageField(upload_to='teachers/', blank=True, null=True)

    def __str__(self):
        return self.user.username

class ParentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    students = models.ManyToManyField(StudentProfile, blank=True)
    def __str__(self):
        return self.user.username