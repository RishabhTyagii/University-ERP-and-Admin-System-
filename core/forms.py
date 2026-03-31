from django import forms
from .models import Course, Student, SemesterResult, SubjectResult, FeeStructure


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'code', 'duration_years', 'total_semesters', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'full_name',
            'roll_number',
            'enrollment_number',
            'dob',
            'email',
            'phone',
            'address',
            'course',
            'semester',
        ]
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }


class FeeStructureForm(forms.ModelForm):
    class Meta:
        model = FeeStructure
        fields = ['course', 'year_or_semester', 'amount', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class SemesterResultForm(forms.ModelForm):
    class Meta:
        model = SemesterResult
        fields = ['student']