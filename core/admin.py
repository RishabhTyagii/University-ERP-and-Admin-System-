from django.contrib import admin
from django.contrib.auth.models import User
from .models import Course, FeeStructure, Student, SemesterResult, SubjectResult, ContactMessage


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'duration_years', 'total_semesters')
    search_fields = ('name', 'code')


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ('course', 'year_or_semester', 'amount')
    list_filter = ('course',)
    search_fields = ('course__name', 'year_or_semester')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        'full_name',
        'roll_number',
        'enrollment_number',
        'course',
        'semester',
        'user',
    )
    list_filter = ('course', 'semester')
    search_fields = (
        'full_name',
        'roll_number',
        'enrollment_number',
        'email',
        'phone',
    )

    fieldsets = (
        ('Student Information', {
            'fields': (
                'user',
                'full_name',
                'roll_number',
                'enrollment_number',
                'dob',
                'email',
                'phone',
                'address',
                'course',
                'semester',
            )
        }),
    )

    def save_model(self, request, obj, form, change):
        username = obj.roll_number.strip()
        password_plain = obj.dob.strftime("%d%m%Y")

        if obj.user:
            user = obj.user
            user.username = username
            user.email = obj.email
            user.first_name = obj.full_name
            user.set_password(password_plain)
            user.save()
            obj.user = user
        else:
            user = User.objects.filter(username=username).first()

            if user:
                user.email = obj.email
                user.first_name = obj.full_name
                user.set_password(password_plain)
                user.save()
            else:
                user = User.objects.create_user(
                    username=username,
                    password=password_plain,
                    email=obj.email,
                    first_name=obj.full_name,
                )

            obj.user = user

        super().save_model(request, obj, form, change)


class SubjectResultInline(admin.TabularInline):
    model = SubjectResult
    extra = 1


@admin.register(SemesterResult)
class SemesterResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'semester', 'sgpa', 'cgpa', 'is_pass', 'published_at')
    list_filter = ('semester', 'is_pass', 'student__course')
    search_fields = ('student__full_name', 'student__roll_number')
    inlines = [SubjectResultInline]


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at')
    search_fields = ('name', 'email')
    readonly_fields = ('created_at',)


admin.site.site_header = "SVSU University Admin"
admin.site.site_title = "SVSU Admin Portal"
admin.site.index_title = "Welcome to SVSU University Admin Panel"