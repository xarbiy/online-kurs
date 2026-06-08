from django.db import models
from django.conf import settings
from courses.models import Subject


class Quiz(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="quizzes", verbose_name="Fan")
    title = models.CharField(max_length=200, verbose_name="Sarlavha")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    time_limit = models.PositiveIntegerField(default=30, verbose_name="Vaqt chegarasi (daqiqa)")
    pass_score = models.PositiveIntegerField(default=70, verbose_name="O'tish bali (%)")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan")

    class Meta:
        verbose_name = "Test"
        verbose_name_plural = "Testlar"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def question_count(self):
        return self.questions.count()


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions", verbose_name="Test")
    text = models.TextField(verbose_name="Savol matni")
    image = models.ImageField(upload_to="questions/", null=True, blank=True, verbose_name="Rasm")
    explanation = models.TextField(blank=True, verbose_name="Tushuntirish")
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib")
    points = models.PositiveIntegerField(default=1, verbose_name="Ball")

    class Meta:
        verbose_name = "Savol"
        verbose_name_plural = "Savollar"
        ordering = ["order"]

    def __str__(self):
        return f"{self.quiz.title}: {self.text[:60]}"


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers", verbose_name="Savol")
    text = models.CharField(max_length=500, verbose_name="Javob matni")
    is_correct = models.BooleanField(default=False, verbose_name="To'g'ri javob")

    class Meta:
        verbose_name = "Javob"
        verbose_name_plural = "Javoblar"

    def __str__(self):
        return f"{self.text} ({'✓' if self.is_correct else '✗'})"


class QuizAttempt(models.Model):
    STATUS_CHOICES = [
        ("in_progress", "Davom etmoqda"),
        ("completed", "Tugallangan"),
        ("timed_out", "Vaqt tugadi"),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="attempts", verbose_name="Foydalanuvchi")
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="attempts", verbose_name="Test")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="in_progress", verbose_name="Holat")
    started_at = models.DateTimeField(auto_now_add=True, verbose_name="Boshlangan")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Tugallangan")

    class Meta:
        verbose_name = "Test urinishi"
        verbose_name_plural = "Test urinishlari"
        ordering = ["-started_at"]


class UserAnswer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name="user_answers", verbose_name="Urinish")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name="Savol")
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Tanlangan javob")

    class Meta:
        verbose_name = "Foydalanuvchi javobi"
        verbose_name_plural = "Foydalanuvchi javoblari"
        unique_together = [["attempt", "question"]]


class QuizResult(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="quiz_results", verbose_name="Foydalanuvchi")
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="results", verbose_name="Test")
    attempt = models.OneToOneField(QuizAttempt, on_delete=models.CASCADE, related_name="result", verbose_name="Urinish")
    score = models.FloatField(verbose_name="Ball (%)")
    correct_answers = models.PositiveIntegerField(default=0, verbose_name="To'g'ri javoblar")
    total_questions = models.PositiveIntegerField(default=0, verbose_name="Jami savollar")
    passed = models.BooleanField(default=False, verbose_name="O'tdi")
    completed_at = models.DateTimeField(auto_now_add=True, verbose_name="Tugallangan")

    class Meta:
        verbose_name = "Test natijasi"
        verbose_name_plural = "Test natijalari"
        ordering = ["-completed_at"]

    def __str__(self):
        return f"{self.user.email} - {self.quiz.title}: {self.score:.1f}%"
