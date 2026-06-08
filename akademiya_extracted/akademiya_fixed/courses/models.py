from django.db import models
from django.conf import settings


class Subject(models.Model):
    name = models.CharField(max_length=100, verbose_name="Fan nomi")
    slug = models.SlugField(unique=True, verbose_name="Slug")
    icon = models.CharField(max_length=50, default="bi-book", verbose_name="Ikonka")
    color = models.CharField(max_length=20, default="#3B82F6", verbose_name="Rang")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib")

    class Meta:
        verbose_name = "Fan"
        verbose_name_plural = "Fanlar"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class Course(models.Model):
    LEVEL_CHOICES = [
        ("beginner", "Boshlang'ich"),
        ("intermediate", "O'rta"),
        ("advanced", "Ilg'or"),
    ]
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="courses", verbose_name="Fan")
    title = models.CharField(max_length=200, verbose_name="Sarlavha")
    slug = models.SlugField(verbose_name="Slug")
    description = models.TextField(verbose_name="Tavsif")
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default="beginner", verbose_name="Daraja")
    cover_image = models.ImageField(upload_to="covers/", null=True, blank=True, verbose_name="Muqova")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan")

    class Meta:
        verbose_name = "Kurs"
        verbose_name_plural = "Kurslar"
        ordering = ["-created_at"]
        unique_together = [["subject", "slug"]]

    def __str__(self):
        return f"{self.subject.name} - {self.title}"

    def lesson_count(self):
        return self.lessons.count()

    def enrolled_count(self):
        return self.enrollments.count()


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons", verbose_name="Kurs")
    title = models.CharField(max_length=200, verbose_name="Sarlavha")
    content = models.TextField(verbose_name="Mazmun")
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib")
    duration_minutes = models.PositiveIntegerField(default=10, verbose_name="Davomiyligi (daqiqa)")
    video_url = models.URLField(blank=True, verbose_name="Video URL")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan")

    class Meta:
        verbose_name = "Dars"
        verbose_name_plural = "Darslar"
        ordering = ["order"]

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Enrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments", verbose_name="Foydalanuvchi")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments", verbose_name="Kurs")
    enrolled_at = models.DateTimeField(auto_now_add=True, verbose_name="Yozilgan sana")
    completed = models.BooleanField(default=False, verbose_name="Tugatilgan")

    class Meta:
        verbose_name = "Yozilish"
        verbose_name_plural = "Yozilishlar"
        unique_together = [["user", "course"]]

    def __str__(self):
        return f"{self.user.email} → {self.course.title}"


class LessonProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="lesson_progress", verbose_name="Foydalanuvchi")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="progress", verbose_name="Dars")
    completed = models.BooleanField(default=False, verbose_name="Tugatilgan")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Tugatilgan vaqt")

    class Meta:
        verbose_name = "Dars jarayoni"
        verbose_name_plural = "Dars jarayonlari"
        unique_together = [["user", "lesson"]]
