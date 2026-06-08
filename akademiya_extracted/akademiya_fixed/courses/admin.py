from django.contrib import admin
from .models import Subject, Course, Lesson, Enrollment, LessonProgress


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "icon", "color", "order")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("order",)
    search_fields = ("name",)


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ("title", "order", "duration_minutes")


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "subject", "level", "enrolled_count", "lesson_count", "is_active", "created_at")
    list_filter = ("subject", "level", "is_active")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [LessonInline]
    list_editable = ("is_active",)

    def enrolled_count(self, obj):
        return obj.enrollments.count()
    enrolled_count.short_description = "Yozilganlar"

    def lesson_count(self, obj):
        return obj.lessons.count()
    lesson_count.short_description = "Darslar"


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order", "duration_minutes")
    list_filter = ("course__subject",)
    search_fields = ("title", "content")


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "enrolled_at", "completed")
    list_filter = ("completed", "enrolled_at")
    search_fields = ("user__email", "course__title")


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "lesson", "completed", "completed_at")
    list_filter = ("completed",)
