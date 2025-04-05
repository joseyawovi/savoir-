from django.urls import path
from main import views

urlpatterns = [
    path('', views.index, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('courses/', views.courses, name='courses'),
    path('dashboard/home/', views.dashboard_home, name='dashboard-home'),
    path('dashboard/profile/', views.profile, name='profile'),
    path('dashboard/courses-enrolled/', views.courses_enrolled, name='courses-enrolled'),
    path('dashboard/courses-uploaded/', views.courses_uploaded, name='courses-uploaded'),
    path('dashboard/modules-uploaded/', views.modules_uploaded, name='modules-uploaded'),

    path('dashboard/upload/', views.upload, name='upload'),
    path('dashboard/<slug:slug>/course-edit/', views.course_edit, name='course-edit'),
    path('dashboard/<slug:slug>/delete/', views.delete_course, name='delete-course'),
    path('<str:instructor>/course/<slug:slug>/', views.course_details, name='course_details'),

    path('dashboard/upload_module/', views.upload_module, name='upload_module'),
    path('<str:instructor>/module/<slug:slug>/', views.module_details, name='module_details'),

    path('dashboard/upload_lesson/', views.upload_lesson, name='upload_lesson'),
    path('<str:instructor>/module/<slug:slug>/', views.module_details, name='module_details'),

    path('<slug:slug>/lesson', views.lesson_details, name='lesson_detail'),
    path('courses/<str:category>/', views.category, name='category'),
]
