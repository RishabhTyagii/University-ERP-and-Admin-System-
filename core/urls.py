from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('courses/', views.courses, name='courses'),
    path('admission-process/', views.admission_process, name='admission_process'),
    path('fee-structure/', views.fee_structure, name='fee_structure'),
    path('contact/', views.contact, name='contact'),
    path('result/', views.result_search, name='result_search'),

    path('student/login/', views.student_login, name='student_login'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/profile/', views.student_profile, name='student_profile'),
    path('student/results/', views.student_results, name='student_results'),
    path('student/logout/', views.student_logout, name='student_logout'),
    path('admin-panel/login/', views.admin_login, name='admin_login'),
    path('admin-panel/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/courses/', views.admin_course_list, name='admin_course_list'),
    path('admin-panel/courses/add/', views.admin_course_add, name='admin_course_add'),
    path('admin-panel/students/', views.admin_student_list, name='admin_student_list'),
    path('admin-panel/students/add/', views.admin_student_add, name='admin_student_add'),
    path('admin-panel/fees/', views.admin_fee_list, name='admin_fee_list'),
    path('admin-panel/fees/add/', views.admin_fee_add, name='admin_fee_add'),
    path('admin-panel/results/', views.admin_result_list, name='admin_result_list'),
    path('admin-panel/results/add/', views.admin_result_add, name='admin_result_add'),
    path('admin-panel/messages/', views.admin_messages, name='admin_messages'),
    path('admin-panel/logout/', views.admin_logout, name='admin_logout'),
    
    
    
    

path('admin-panel/students/<int:student_id>/', views.admin_student_detail, name='admin_student_detail'),
path('admin-panel/results/<int:result_id>/', views.admin_semester_result_detail, name='admin_semester_result_detail'),
path('admin-panel/students/<int:student_id>/results/add/', views.admin_result_add, name='admin_result_add'),
]