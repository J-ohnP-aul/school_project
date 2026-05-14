from django.db import models

# Create your models here.

from accounts.models import (
    StudentProfile,
    TeacherProfile
)


class Assignment(models.Model):

    teacher = models.ForeignKey(
        TeacherProfile,
        on_delete=models.CASCADE
    )

    title = models.CharField(
        max_length=200
    )

    description = models.TextField()

    due_date = models.DateField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title


class Grade(models.Model):

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='student_grades'
    )

    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE
    )

    score = models.DecimalField(
        max_digits=5,
        decimal_places=2
    )

    remarks = models.TextField(
        blank=True
    )

    def __str__(self):
        return f'{self.student} - {self.assignment}'


class Attendance(models.Model):

    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
    ]

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE
    )

    date = models.DateField()

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES
    )

    recorded_by = models.ForeignKey(
        TeacherProfile,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.student} - {self.date}'