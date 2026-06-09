from django.db import models

# Create your models here.

class Assignment(models.Model):

    teacher = models.ForeignKey(
        'accounts.TeacherProfile',
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
        'accounts.StudentProfile',
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
        'accounts.StudentProfile',
        on_delete=models.CASCADE
    )

    date = models.DateField()

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES
    )

    recorded_by = models.ForeignKey(
        'accounts.TeacherProfile',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.student} - {self.date}'
    

#fee structure 

class FeeStructure(models.Model):
    LEVEL_PLAYGROUP = 'Playgroup'
    LEVEL_PRIMARY = 'Primary'
    LEVEL_JUNIOR_SECONDARY = 'Junior Secondary'
    LEVEL_BOARDING = 'Boarding'

    LEVEL_CHOICES = [
        (LEVEL_PLAYGROUP, 'Playgroup'),
        (LEVEL_PRIMARY, 'Primary'),
        (LEVEL_JUNIOR_SECONDARY, 'Junior Secondary'),
        (LEVEL_BOARDING, 'Boarding'),
    ]

    TERM_1 = 'Term 1'
    TERM_2 = 'Term 2'
    TERM_3 = 'Term 3'

    TERM_CHOICES = [
        (TERM_1, 'Term 1'),
        (TERM_2, 'Term 2'),
        (TERM_3, 'Term 3'),
    ]

    level = models.CharField(max_length=24, choices=LEVEL_CHOICES)
    term = models.CharField(max_length=16, choices=TERM_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    year = models.IntegerField(default=2025)
    notes = models.TextField(blank=True, help_text='Optional note for this fee line item.')

    class Meta:
        ordering = ['year', 'level', 'term']
        verbose_name = 'Fee Structure'
        verbose_name_plural = 'Fee Structures'

    def __str__(self):
        return f'{self.level} • {self.term} • {self.year}'


class AcademicProgram(models.Model):
    name = models.CharField(max_length=140)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Academic Advantage'
        verbose_name_plural = 'Academic Advantages'

    def __str__(self):
        return self.name


class Requirement(models.Model):
    name = models.CharField(max_length=140)

    class Meta:
        verbose_name = 'Requirement'
        verbose_name_plural = 'Requirements'

    def __str__(self):
        return self.name

class GradeLevel(models.Model):
    name = models.CharField(
        max_length=30,
        unique=True
    )

    def __str__(self):
        return self.name


class Term(models.Model):
    name = models.CharField(
        max_length=20,
        unique=True
    )
    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True
    )

    def __str__(self):
        return self.name
    
class Competency(models.Model): #math, comp subjects ...
    name = models.CharField(
        max_length=100,
        unique=True
    )
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
    
class Assessment(models.Model):
    BAND_EE = 'EE'
    BAND_ME = 'ME'
    BAND_AE = 'AE'
    BAND_BE = 'BE'
    
    PERFOMANCE_CHOICES = [
        (BAND_EE, 'Exceeding Expectations'),
        (BAND_ME, 'Meeting Expectations'),
        (BAND_AE, 'Approaching Expectations'),
        (BAND_BE, 'Below Expectations'),
    ]
    student = models.ForeignKey(
        'accounts.StudentProfile',
        on_delete=models.CASCADE
    )
    teacher = models.ForeignKey(
        'accounts.TeacherProfile',
        on_delete=models.CASCADE
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE
    )
    competency = models.ForeignKey(
        Competency, 
        on_delete=models.CASCADE
    )
    term = models.ForeignKey(
        Term,
        on_delete=models.CASCADE
    )
    perfomance_band = models.CharField(
        max_length=2,
        choices=PERFOMANCE_CHOICES
    )
    remarks = models.TextField(blank=True)
    assessed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return  (
            f'{self.student} - '
            f'{self.subject} - '
            f'{self.perfomance_band}'
        )
    class Meta:
        unique_together = [
            'student',
            'subject',
            'competency',
            'term'
        ]
    
class DraftAssessment(models.Model):
    teacher = models.ForeignKey(
        'accounts.TeacherProfile',
        on_delete=models.CASCADE,
        related_name='assessment_drafts'
    )
    grade = models.CharField(max_length=50)  # e.g., "Grade 7"
    stream = models.CharField(max_length=30, blank=True)  # e.g., "A" or blank for all
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE)
    competency = models.ForeignKey('Competency', on_delete=models.CASCADE)
    term = models.ForeignKey('Term', on_delete=models.CASCADE)
    
    # Stores draft data as JSON: {student_id: {"percentage": 68, "remarks": "good work", "absent": false}}
    draft_data = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        unique_together = ['teacher', 'grade', 'stream', 'subject', 'competency', 'term']
    
    def __str__(self):
        stream_display = f" - {self.stream}" if self.stream else ""
        return f"Draft: {self.grade}{stream_display} - {self.subject.name} ({self.teacher.user.username})"
    
    def get_completion_count(self):
        """Returns number of students with scores entered"""
        from accounts.models import StudentProfile
        
        # Get total students for this gs
        students = StudentProfile.objects.filter(grade=self.grade)
        if self.stream:
            students = students.filter(stream=self.stream)
        
        total = students.count()
        filled = len([s for s in self.draft_data.values() if s.get('percentage')])
        
        return filled, total