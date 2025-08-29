from django import forms
from .models import Course, Chapter, Lesson

class CourseEditForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ('title', 'description', 'thumbnail', 'featured_video', 'level', 'duration', 'category', 'requirements', 'content', 'price', 'discount')

class ChapterForm(forms.ModelForm):
    class Meta:
        model = Chapter
        fields = ('title', 'description', 'order')

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ('title', 'description', 'youtube_url', 'order', 'duration')
