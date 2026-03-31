from django.db import models
from django.contrib.auth.models import User


class Course(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    duration_years = models.PositiveIntegerField(default=4)
    total_semesters = models.PositiveIntegerField(default=8)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class FeeStructure(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    year_or_semester = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.course.name} - {self.year_or_semester}"


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    full_name = models.CharField(max_length=200)
    roll_number = models.CharField(max_length=50, unique=True)
    enrollment_number = models.CharField(max_length=50, unique=True)
    dob = models.DateField()

    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True)
    semester = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.full_name} ({self.roll_number})"


class SemesterResult(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='semester_results'
    )
    semester = models.PositiveIntegerField()

    sgpa = models.FloatField(default=0, blank=True, null=True)
    cgpa = models.FloatField(default=0, blank=True, null=True)
    is_pass = models.BooleanField(default=False)

    published_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'semester')
        ordering = ['semester']

    def __str__(self):
        return f"{self.student.roll_number} - Semester {self.semester}"

    def calculate_sgpa(self):
        subjects = self.subject_results.filter(is_extra_subject=False)

        counted_subjects = subjects.count()
        if counted_subjects == 0:
            return 0

        total_grade_points = sum(subject.grade_point for subject in subjects)
        return round(total_grade_points / counted_subjects, 2)

    def calculate_cgpa(self):
        semester_results = SemesterResult.objects.filter(student=self.student).order_by('semester')
        sgpas = [sem.sgpa for sem in semester_results if sem.sgpa is not None]

        if not sgpas:
            return 0

        return round(sum(sgpas) / len(sgpas), 2)

    def check_pass_status(self):
        normal_subjects = self.subject_results.filter(is_extra_subject=False)

        if not normal_subjects.exists():
            return False

        return all(subject.is_pass for subject in normal_subjects)

    def update_student_semester(self):
        if not self.is_pass:
            return

        if not self.student.course:
            return

        max_semesters = self.student.course.total_semesters
        next_semester = self.semester + 1

        if self.student.semester <= self.semester and next_semester <= max_semesters:
            self.student.semester = next_semester
            self.student.save(update_fields=['semester'])

    def recalculate(self):
        self.is_pass = self.check_pass_status()
        self.sgpa = self.calculate_sgpa()
        self.cgpa = self.calculate_cgpa()
        super().save(update_fields=['is_pass', 'sgpa', 'cgpa'])
        self.update_student_semester()

        cgpa_value = self.calculate_cgpa()
        SemesterResult.objects.filter(student=self.student).update(cgpa=cgpa_value)


class SubjectResult(models.Model):
    semester_result = models.ForeignKey(
        SemesterResult,
        on_delete=models.CASCADE,
        related_name='subject_results'
    )

    subject_name = models.CharField(max_length=200)
    is_extra_subject = models.BooleanField(default=False)

    external_marks = models.PositiveIntegerField(default=0)
    internal_marks = models.PositiveIntegerField(default=0)

    total_marks = models.PositiveIntegerField(default=0, blank=True, null=True)
    grade = models.CharField(max_length=10, blank=True)
    grade_point = models.FloatField(default=0, blank=True, null=True)
    is_pass = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.subject_name} - Sem {self.semester_result.semester}"

    def calculate_grade(self, total):
        if total >= 90:
            return "A+", 10
        elif total >= 80:
            return "A", 9
        elif total >= 70:
            return "B+", 8
        elif total >= 60:
            return "B", 7
        elif total >= 50:
            return "C", 6
        elif total >= 40:
            return "D", 5
        else:
            return "F", 0

    def save(self, *args, **kwargs):
        if self.is_extra_subject:
            if self.external_marks > 100:
                self.external_marks = 100

            self.internal_marks = 0
            self.total_marks = self.external_marks
            self.is_pass = self.external_marks >= 40
        else:
            if self.external_marks > 70:
                self.external_marks = 70

            if self.internal_marks > 30:
                self.internal_marks = 30

            self.total_marks = self.external_marks + self.internal_marks
            self.is_pass = (
                self.external_marks >= 21 and
                self.internal_marks >= 10 and
                self.total_marks >= 40
            )

        self.grade, self.grade_point = self.calculate_grade(self.total_marks)
        super().save(*args, **kwargs)

        self.semester_result.recalculate()
        
class ContactMessage(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    
    
    
    
    
    
    
    
    
    
    