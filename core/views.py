from django.contrib.auth.decorators import user_passes_test,login_required
from django.forms import modelformset_factory
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Q
from .forms import CourseForm, StudentForm, FeeStructureForm, SemesterResultForm
from .models import (
    Course,
    FeeStructure,
    ContactMessage,
    Student,
    SemesterResult,
    SubjectResult,
)
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

def is_admin_user(user):
    return user.is_authenticated and user.is_staff

def home(request):
    return render(request, 'home.html')


def about(request):
    return render(request, 'about.html')


def courses(request):
    courses_list = Course.objects.all()
    return render(request, 'courses.html', {'courses': courses_list})


def admission_process(request):
    return render(request, 'admission_process.html')


def fee_structure(request):
    fees = FeeStructure.objects.select_related('course').all()
    return render(request, 'fee_structure.html', {'fees': fees})


def contact(request):
    success = False

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        if name and email and message:
            ContactMessage.objects.create(
                name=name,
                email=email,
                message=message
            )
            success = True

    return render(request, 'contact.html', {'success': success})


def result_search(request):
    error = None

    if request.method == 'POST':
        roll_number = request.POST.get('roll_number')
        dob = request.POST.get('dob')

        try:
            student = Student.objects.select_related('course').get(
                roll_number=roll_number,
                dob=dob
            )
            results = SemesterResult.objects.filter(student=student).prefetch_related('subject_results').order_by('semester')

            if results.exists():
                return render(request, 'result_detail.html', {
                    'student': student,
                    'results': results
                })
            else:
                error = "Result not found for this student."

        except Student.DoesNotExist:
            error = "Invalid Roll Number or DOB."

    return render(request, 'result_search.html', {'error': error})


def student_login(request):
    error = None

    if request.user.is_authenticated:
        return redirect('student_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            try:
                Student.objects.get(user=user)
                login(request, user)
                return redirect('student_dashboard')
            except Student.DoesNotExist:
                error = "This user is not linked with any student account."
        else:
            error = "Invalid username or password."

    return render(request, 'student/login.html', {'error': error})


@login_required
def student_dashboard(request):
    student = Student.objects.select_related('course').filter(user=request.user).first()

    if not student:
        return redirect('student_login')

    results = SemesterResult.objects.filter(student=student).prefetch_related('subject_results').order_by('semester')
    latest_result = results.last()

    context = {
        'student': student,
        'results': results,
        'latest_result': latest_result,
    }
    return render(request, 'student/dashboard.html', context)


@login_required
def student_profile(request):
    student = Student.objects.select_related('course').filter(user=request.user).first()

    if not student:
        return redirect('student_login')

    return render(request, 'student/profile.html', {'student': student})


@login_required
def student_results(request):
    student = Student.objects.select_related('course').filter(user=request.user).first()

    if not student:
        return redirect('student_login')

    results = SemesterResult.objects.filter(student=student).prefetch_related('subject_results').order_by('semester')

    return render(request, 'student/my_results.html', {
        'student': student,
        'results': results
    })


@login_required
def student_logout(request):
    logout(request)
    return redirect('student_login')



from django.contrib.auth import authenticate, login, logout
from django.forms import modelformset_factory
from django.shortcuts import get_object_or_404


def admin_login(request):
    error = None

    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            error = "Invalid admin credentials."

    return render(request, 'admin_panel/login.html', {'error': error})


@user_passes_test(is_admin_user)
def admin_dashboard(request):
    context = {
        'total_courses': Course.objects.count(),
        'total_students': Student.objects.count(),
        'total_results': SemesterResult.objects.count(),
        'total_fees': FeeStructure.objects.count(),
        'total_messages': ContactMessage.objects.count(),
    }
    return render(request, 'admin_panel/dashboard.html', context)


@user_passes_test(is_admin_user)
def admin_course_list(request):
    courses = Course.objects.all().order_by('name')
    return render(request, 'admin_panel/course_list.html', {'courses': courses})


@user_passes_test(is_admin_user)
def admin_course_add(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_course_list')
    else:
        form = CourseForm()

    return render(request, 'admin_panel/course_form.html', {'form': form, 'title': 'Add Course'})


@user_passes_test(is_admin_user)
def admin_student_list(request):
    query = request.GET.get('q', '').strip()

    students = Student.objects.select_related('course').all().order_by('full_name')

    if query:
        students = students.filter(
            Q(full_name__icontains=query) |
            Q(roll_number__icontains=query) |
            Q(enrollment_number__icontains=query)
        )

    return render(request, 'admin_panel/student_list.html', {
        'students': students,
        'query': query,
    })


@user_passes_test(is_admin_user)
def admin_student_add(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save()

            # auto user create/update
            username = student.roll_number.strip()
            password_plain = student.dob.strftime("%d%m%Y")

            user = student.user
            if user:
                user.username = username
                user.email = student.email
                user.first_name = student.full_name
                user.set_password(password_plain)
                user.save()
            else:
                from django.contrib.auth.models import User
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': student.email,
                        'first_name': student.full_name
                    }
                )
                user.email = student.email
                user.first_name = student.full_name
                user.set_password(password_plain)
                user.save()

                student.user = user
                student.save()

            return redirect('admin_student_list')
    else:
        form = StudentForm()

    return render(request, 'admin_panel/student_form.html', {'form': form, 'title': 'Add Student'})


@user_passes_test(is_admin_user)
def admin_fee_list(request):
    fees = FeeStructure.objects.select_related('course').all().order_by('course__name')
    return render(request, 'admin_panel/fee_list.html', {'fees': fees})


@user_passes_test(is_admin_user)
def admin_fee_add(request):
    if request.method == 'POST':
        form = FeeStructureForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_fee_list')
    else:
        form = FeeStructureForm()

    return render(request, 'admin_panel/fee_form.html', {'form': form, 'title': 'Add Fee Structure'})


@user_passes_test(is_admin_user)
def admin_result_list(request):
    results = SemesterResult.objects.select_related('student', 'student__course').all().order_by('-semester')
    return render(request, 'admin_panel/result_list.html', {'results': results})


@user_passes_test(is_admin_user)
def admin_result_add(request, student_id):
    student = get_object_or_404(
        Student.objects.select_related('course'),
        id=student_id
    )

    max_semesters = student.course.total_semesters if student.course else 0
    existing_semesters = set(
        SemesterResult.objects.filter(student=student).values_list('semester', flat=True)
    )

    allowed_semesters = [
        (sem, f"Semester {sem}")
        for sem in range(1, max_semesters + 1)
        if sem not in existing_semesters
    ]

    SubjectResultFormSet = modelformset_factory(
        SubjectResult,
        fields=('subject_name', 'is_extra_subject', 'external_marks', 'internal_marks'),
        extra=6,
        can_delete=False
    )

    if request.method == 'POST':
        result_form = SemesterResultForm(request.POST)
        result_form.fields['semester'].choices = allowed_semesters

        formset = SubjectResultFormSet(
            request.POST,
            queryset=SubjectResult.objects.none()
        )

        if result_form.is_valid() and formset.is_valid():
            semester_result = result_form.save(commit=False)
            semester_result.student = student
            semester_result.save()

            created_any_subject = False

            for form in formset:
                if form.cleaned_data:
                    subject_name = form.cleaned_data.get('subject_name')
                    if subject_name:
                        subject = form.save(commit=False)
                        subject.semester_result = semester_result
                        subject.save()
                        created_any_subject = True

            if created_any_subject:
                semester_result.recalculate()
            else:
                semester_result.delete()

            return redirect('admin_student_detail', student_id=student.id)
    else:
        result_form = SemesterResultForm()
        result_form.fields['semester'].choices = allowed_semesters
        formset = SubjectResultFormSet(queryset=SubjectResult.objects.none())

    return render(request, 'admin_panel/result_form.html', {
        'result_form': result_form,
        'formset': formset,
        'title': f'Add Result - {student.full_name}',
        'student': student,
        'allowed_semesters': allowed_semesters,
    })

@user_passes_test(is_admin_user)
def admin_messages(request):
    messages = ContactMessage.objects.all().order_by('-created_at')
    return render(request, 'admin_panel/messages.html', {'messages': messages})


@user_passes_test(is_admin_user)
def admin_logout(request):
    logout(request)
    return redirect('admin_login')

@user_passes_test(is_admin_user)
def admin_student_detail(request, student_id):
    student = get_object_or_404(
        Student.objects.select_related('course'),
        id=student_id
    )

    semester_results = (
        SemesterResult.objects
        .filter(student=student)
        .prefetch_related('subject_results')
        .order_by('semester')
    )

    max_semesters = student.course.total_semesters if student.course else 0
    existing_semesters = set(semester_results.values_list('semester', flat=True))

    available_semesters = [
        sem for sem in range(1, max_semesters + 1)
        if sem not in existing_semesters
    ]

    return render(request, 'admin_panel/student_detail.html', {
        'student': student,
        'semester_results': semester_results,
        'available_semesters': available_semesters,
        'max_semesters': max_semesters,
    })
    
    
@user_passes_test(is_admin_user)
def admin_semester_result_detail(request, result_id):
    result = get_object_or_404(
        SemesterResult.objects.select_related('student', 'student__course').prefetch_related('subject_results'),
        id=result_id
    )

    return render(request, 'admin_panel/result_detail.html', {
        'result': result
    })