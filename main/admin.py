from django.contrib import admin
from .models import library, Course, Enrollment, Chapter, Lesson, LessonProgress, Certificate

class ChapterInline(admin.TabularInline):
    model = Chapter
    extra = 1
    fields = ('title', 'description', 'order')

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ('title', 'youtube_url', 'order', 'duration')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'category', 'level', 'created_at')
    list_filter = ('category', 'level', 'created_at')
    search_fields = ('title', 'instructor__username')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ChapterInline]

@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'created_at')
    list_filter = ('course', 'created_at')
    search_fields = ('title', 'course__title')
    inlines = [LessonInline]

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'chapter', 'order', 'duration', 'created_at')
    list_filter = ('chapter__course', 'created_at')
    search_fields = ('title', 'chapter__title', 'chapter__course__title')

@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'completed', 'completed_at')
    list_filter = ('completed', 'completed_at', 'lesson__chapter__course')
    search_fields = ('user__username', 'lesson__title')

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'certificate_id', 'issued_at')
    list_filter = ('issued_at', 'course')
    search_fields = ('user__username', 'course__title', 'certificate_id')
    readonly_fields = ('certificate_id', 'issued_at')

admin.site.register(library)
admin.site.register(Enrollment)