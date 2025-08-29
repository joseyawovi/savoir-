from django.db import models
from cloudinary.models import CloudinaryField
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.urls import reverse
import re

# Create your models here.

class library(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    image = CloudinaryField('image')

class Course(models.Model):
    LEVEL_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced')
    ]

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    thumbnail = CloudinaryField('thumbnail')
    featured_video = CloudinaryField('featured_video')
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses', default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='Beginner')
    duration = models.CharField(max_length=10, default='0')
    category = models.CharField(max_length=255, default="uncategorized")
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    requirements = models.TextField(help_text='Enter the requirements for the course, separated by a comma.', default='')
    content = models.TextField(help_text='Enter the course content, separated by a comma.', default='')

    students = models.ManyToManyField(User, related_name='enrolled_courses', blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_instructor_username(self):
        return self.instructor.username
    
    def get_requirements_list(self):
        return [req.strip() for req in self.requirements.split(',') if req.strip()]

    def get_content_list(self):
        return [content.strip() for content in self.content.split(',') if content.strip()]
    
    def get_total_lessons(self):
        return Lesson.objects.filter(chapter__course=self).count()
    
    def get_progress_percentage(self, user):
        if not user.is_authenticated:
            return 0
        total_lessons = self.get_total_lessons()
        if total_lessons == 0:
            return 0
        completed_lessons = LessonProgress.objects.filter(
            user=user, lesson__chapter__course=self, completed=True
        ).count()
        return int((completed_lessons / total_lessons) * 100)
    
    def is_completed_by_user(self, user):
        if not user.is_authenticated:
            return False
        total_lessons = self.get_total_lessons()
        if total_lessons == 0:
            return False
        completed_lessons = LessonProgress.objects.filter(
            user=user, lesson__chapter__course=self, completed=True
        ).count()
        return completed_lessons >= total_lessons
    
class Chapter(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='chapters')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
        unique_together = ['course', 'order']
    
    def __str__(self):
        return f'{self.course.title} - Chapter {self.order}: {self.title}'
    
    def get_lessons_count(self):
        return self.lessons.count()

class Lesson(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    youtube_url = models.URLField(help_text='YouTube video URL')
    order = models.PositiveIntegerField(default=1)
    duration = models.CharField(max_length=20, help_text='Duration in format like "15:30"', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
        unique_together = ['chapter', 'order']
    
    def __str__(self):
        return f'{self.chapter.course.title} - {self.chapter.title} - Lesson {self.order}: {self.title}'
    
    def get_youtube_embed_id(self):
        """Extract YouTube video ID from URL for embedding"""
        youtube_regex = r'(?:youtube\.com\/(?:[^\/]+\/.+\/|\/watch\?v=|watch\?feature=player_embedded&v=|embed\/|user\/[^\/]+\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
        match = re.search(youtube_regex, self.youtube_url)
        return match.group(1) if match else None
    
    def get_next_lesson(self):
        """Get the next lesson in the course sequence"""
        # Try to get next lesson in the same chapter
        next_in_chapter = Lesson.objects.filter(
            chapter=self.chapter, order__gt=self.order
        ).first()
        
        if next_in_chapter:
            return next_in_chapter
        
        # If no next lesson in chapter, get first lesson of next chapter
        next_chapter = Chapter.objects.filter(
            course=self.chapter.course, order__gt=self.chapter.order
        ).first()
        
        if next_chapter:
            return next_chapter.lessons.first()
        
        return None
    
    def get_previous_lesson(self):
        """Get the previous lesson in the course sequence"""
        # Try to get previous lesson in the same chapter
        prev_in_chapter = Lesson.objects.filter(
            chapter=self.chapter, order__lt=self.order
        ).last()
        
        if prev_in_chapter:
            return prev_in_chapter
        
        # If no previous lesson in chapter, get last lesson of previous chapter
        prev_chapter = Chapter.objects.filter(
            course=self.chapter.course, order__lt=self.chapter.order
        ).last()
        
        if prev_chapter:
            return prev_chapter.lessons.last()
        
        return None
    
    def is_completed_by_user(self, user):
        if not user.is_authenticated:
            return False
        return LessonProgress.objects.filter(
            user=user, lesson=self, completed=True
        ).exists()

class LessonProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress')
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'lesson']
    
    def __str__(self):
        status = 'Completed' if self.completed else 'In Progress'
        return f'{self.user.username} - {self.lesson.title} ({status})'

class Certificate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='certificates')
    issued_at = models.DateTimeField(auto_now_add=True)
    certificate_id = models.CharField(max_length=50, unique=True)
    
    class Meta:
        unique_together = ['user', 'course']
    
    def __str__(self):
        return f'Certificate for {self.user.username} - {self.course.title}'
    
    def save(self, *args, **kwargs):
        if not self.certificate_id:
            import uuid
            self.certificate_id = f'CERT-{uuid.uuid4().hex[:8].upper()}'
        super().save(*args, **kwargs)

class Enrollment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.student.username} enrolled in {self.course.title}'