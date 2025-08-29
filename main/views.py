import cloudinary
import cloudinary.uploader
import cloudinary.api

from django.shortcuts import render, redirect

from django.utils.text import slugify
from .models import Course, Enrollment, Chapter, Lesson, LessonProgress, Certificate
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import CourseEditForm, ChapterForm, LessonForm
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
import pytz
import json

# Create your views here.


def index(request):
    courses = Course.objects.all()[:6]
    return render(request, 'index.html', {'courses': courses})


def about(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'contact.html')


def courses(request):
    courses = Course.objects.all()
    return render(request, 'courses.html', {'courses': courses})

# def profile(request):
#     user = request.user
#     if user.is_authenticated:
#         # get first and last name
#         first_name = user.first_name
#         last_name = user.last_name

#         # get username and email
#         username = user.username
#         email = user.email

#         # get profile picture
#         profile_picture = None
#         if hasattr(user, 'profile'):
#             profile_picture = user.profile.picture

#         return render(request, 'account/dashboard/profile.html', {'first_name': first_name, 'last_name': last_name, 'username': username, 'email': email, 'profile_picture': profile_picture})
#     else:
#         return redirect('account_login')


def dashboard_home(request):
    user = request.user
    courses_uploaded = Course.objects.filter(instructor=user)
    num_courses_uploaded = courses_uploaded.count()
    courses_enrolled = Course.objects.filter(students=user)
    num_courses_enrolled = courses_enrolled.count()
    num_students = Enrollment.objects.filter(course__in=courses_uploaded).values('student').distinct().count()
    
    instructor = request.user
    courses = Course.objects.filter(instructor=instructor)

    enrollments = []
    ist_tz = pytz.timezone('Asia/Kolkata')

    for course in courses:
        course_enrollments = Enrollment.objects.filter(course=course)
        for enrollment in course_enrollments:
            student = enrollment.student
            enrollment_date_ist = enrollment.enrolled_at.astimezone(ist_tz)
            enrollment_date = enrollment_date_ist.strftime('%d %B %Y %H:%M:%S')
            enrollments.append({'course_title': course.title, 'student_name': student.username, 'enrollment_date': enrollment_date})

    context = {
        'courses_uploaded': courses_uploaded,
        'num_courses_uploaded': num_courses_uploaded,
        'num_courses_enrolled': num_courses_enrolled,
        'num_students': num_students,
        'enrollments': enrollments,
    }
    return render(request, 'dashboard/home.html', context)


def profile(request):
    user = request.user
    email = user.email
    full_name = f"{user.first_name} {user.last_name}"
    username = user.username
    return render(request, 'dashboard/profile.html', {'email': email, 'full_name': full_name, 'username': username})


def courses_enrolled(request):
    user = request.user
    courses = Course.objects.filter(students=user)
    context = {
        'courses': courses
    }
    return render(request, 'dashboard/courses-enrolled.html', context)


def courses_uploaded(request):
    courses = Course.objects.filter(instructor=request.user)
    return render(request, 'dashboard/courses-uploaded.html', {'courses': courses})

@login_required
def upload(request):
    if request.method == 'POST':
        try:
            # Get form data
            title = request.POST.get('title')
            description = request.POST.get('description')
            thumbnail = request.FILES.get('thumbnail')
            featured_video = request.FILES.get('featured_video')
            
            # Validate required files
            if not all([thumbnail, featured_video]):
                messages.error(request, "Thumbnail and featured video are required")
                return redirect('upload')
            
            # Upload files to Cloudinary
            thumbnail_upload = cloudinary.uploader.upload(thumbnail)
            featured_video_upload = cloudinary.uploader.upload(
                featured_video, 
                resource_type="video"
            )
            
            # Create course
            course = Course(
                title=title,
                description=description,
                thumbnail=thumbnail_upload['secure_url'],
                featured_video=featured_video_upload['secure_url'],
                instructor=request.user,
                category=request.POST.get('category', 'uncategorized'),
                level=request.POST.get('level', 'Beginner'),
                requirements=request.POST.get('requirements', ''),
                content=request.POST.get('content', ''),
                price=request.POST.get('price', 0),
                discount=request.POST.get('discount', 0),
            )
            course.save()
            
            messages.success(request, "Course uploaded successfully!")
            return redirect('dashboard')  # Redirect to success page
            
        except cloudinary.exceptions.Error as e:
            messages.error(request, f"Cloudinary upload failed: {e}")
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
        
    return render(request, 'dashboard/upload.html')

# def course_details(request, instructor, slug):
#     instructor_obj = get_object_or_404(User, username=instructor)
#     course = get_object_or_404(Course, slug=slug, instructor=instructor_obj)
#     context = {
#         'course': course
#     }
#     return render(request, 'course.html', context)

def course_details(request, instructor, slug):
    instructor_obj = get_object_or_404(User, username=instructor)
    course = get_object_or_404(Course, slug=slug, instructor=instructor_obj)
    category_courses = Course.objects.filter(category__iexact=course.category).exclude(id=course.id)[:3]
    
    # Get course chapters and lessons for preview
    chapters = Chapter.objects.filter(course=course).prefetch_related('lessons')[:3]  # Show first 3 chapters as preview
    total_lessons = course.get_total_lessons()

    enrolled = False
    progress_percentage = 0
    has_certificate = False
    
    if request.user.is_authenticated:
        enrolled = course.students.filter(id=request.user.id).exists()
        if enrolled:
            progress_percentage = course.get_progress_percentage(request.user)
            has_certificate = Certificate.objects.filter(user=request.user, course=course).exists()

    if request.method == 'POST' and not enrolled and request.user.is_authenticated:
        user = request.user
        course.students.add(user)
        enrollment = Enrollment(student=user, course=course)
        enrollment.save()
        messages.success(request, 'You have enrolled in this course!')
        return redirect('course_details', instructor=instructor, slug=slug)

    context = {
        'course': course,
        'enrolled': enrolled,
        'category_courses': category_courses,
        'chapters': chapters,
        'total_lessons': total_lessons,
        'progress_percentage': progress_percentage,
        'has_certificate': has_certificate,
    }
    return render(request, 'course.html', context)

@login_required
def course_edit(request, slug):
    course = get_object_or_404(Course, slug=slug, instructor=request.user)
    if request.method == 'POST':
        form = CourseEditForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
    else:
        form = CourseEditForm(instance=course)
    return render(request, 'dashboard/course-edit.html', {'form': form, 'course': course})

@login_required
def delete_course(request, slug):
    course = get_object_or_404(Course, slug=slug, instructor=request.user)
    if request.method == 'POST':
        course.delete()
        return redirect('/dashboard/courses-uploaded')
    context = {
        'course': course,
    }
    return render(request, 'dashboard/course-edit.html', context)

def category(request, category):
    courses = Course.objects.filter(category__iexact=category)
    context = {
        'category': category,
        'courses': courses
    }
    return render(request, 'category.html', context)


@login_required
def lesson_detail(request, course_slug, lesson_id):
    course = get_object_or_404(Course, slug=course_slug)
    lesson = get_object_or_404(Lesson, id=lesson_id, chapter__course=course)
    
    # Check if user is enrolled in the course
    if not course.students.filter(id=request.user.id).exists():
        messages.error(request, 'You must be enrolled in this course to view lessons.')
        return redirect('course_details', instructor=course.instructor.username, slug=course.slug)
    
    # Get or create lesson progress
    progress, created = LessonProgress.objects.get_or_create(
        user=request.user,
        lesson=lesson,
        defaults={'completed': False}
    )
    
    # Get all lessons in the course for navigation
    chapters = Chapter.objects.filter(course=course).prefetch_related('lessons')
    
    context = {
        'course': course,
        'lesson': lesson,
        'progress': progress,
        'chapters': chapters,
        'next_lesson': lesson.get_next_lesson(),
        'previous_lesson': lesson.get_previous_lesson(),
    }
    return render(request, 'lesson_detail.html', context)

@login_required
def complete_lesson(request, lesson_id):
    if request.method == 'POST':
        lesson = get_object_or_404(Lesson, id=lesson_id)
        
        # Check if user is enrolled in the course
        if not lesson.chapter.course.students.filter(id=request.user.id).exists():
            return JsonResponse({'success': False, 'error': 'Not enrolled in course'})
        
        # Mark lesson as completed
        progress, created = LessonProgress.objects.get_or_create(
            user=request.user,
            lesson=lesson,
            defaults={'completed': True, 'completed_at': timezone.now()}
        )
        
        if not progress.completed:
            progress.completed = True
            progress.completed_at = timezone.now()
            progress.save()
        
        # Check if course is completed
        course = lesson.chapter.course
        if course.is_completed_by_user(request.user):
            # Generate certificate if not already exists
            certificate, cert_created = Certificate.objects.get_or_create(
                user=request.user,
                course=course
            )
            return JsonResponse({
                'success': True, 
                'course_completed': True,
                'certificate_id': certificate.certificate_id
            })
        
        return JsonResponse({'success': True, 'course_completed': False})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def course_curriculum(request, instructor, slug):
    instructor_obj = get_object_or_404(User, username=instructor)
    course = get_object_or_404(Course, slug=slug, instructor=instructor_obj)
    
    # Check if user is enrolled
    if not course.students.filter(id=request.user.id).exists():
        messages.error(request, 'You must be enrolled in this course to view the curriculum.')
        return redirect('course_details', instructor=instructor, slug=slug)
    
    chapters = Chapter.objects.filter(course=course).prefetch_related('lessons')
    
    # Get user's progress
    user_progress = {}
    for chapter in chapters:
        for lesson in chapter.lessons.all():
            progress = LessonProgress.objects.filter(
                user=request.user, lesson=lesson
            ).first()
            user_progress[lesson.id] = progress.completed if progress else False
    
    context = {
        'course': course,
        'chapters': chapters,
        'user_progress': user_progress,
        'progress_percentage': course.get_progress_percentage(request.user),
    }
    return render(request, 'course_curriculum.html', context)

@login_required
def certificate_view(request, certificate_id):
    certificate = get_object_or_404(Certificate, certificate_id=certificate_id, user=request.user)
    
    context = {
        'certificate': certificate,
        'course': certificate.course,
        'user': request.user,
    }
    return render(request, 'certificate.html', context)

def lesson_details(request, slug):
    # Redirect to course curriculum instead
    course = get_object_or_404(Course, slug=slug)
    return redirect('course_curriculum', instructor=course.instructor.username, slug=slug)