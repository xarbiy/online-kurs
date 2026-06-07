from django.contrib import admin
from django.utils.html import format_html
from .models import Quiz, Question, Answer, QuizAttempt, QuizResult


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4
    fields = ("text", "is_correct")


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    fields = ("text", "order", "points", "explanation")


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "subject", "question_count", "time_limit", "pass_score", "is_active", "created_at")
    list_filter = ("subject", "is_active")
    search_fields = ("title",)
    list_editable = ("is_active",)
    inlines = [QuestionInline]

    def question_count(self, obj):
        return obj.questions.count()
    question_count.short_description = "Savollar"


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text_short", "quiz", "order", "points")
    list_filter = ("quiz__subject",)
    search_fields = ("text",)
    inlines = [AnswerInline]

    def text_short(self, obj):
        return obj.text[:80]
    text_short.short_description = "Savol"


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("text", "question", "is_correct_display")
    list_filter = ("is_correct",)

    def is_correct_display(self, obj):
        if obj.is_correct:
            return format_html('<span style="color:green;font-weight:bold">✓ To\'g\'ri</span>')
        return format_html('<span style="color:red">✗ Noto\'g\'ri</span>')
    is_correct_display.short_description = "Holat"


@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    list_display = ("user", "quiz", "score_display", "correct_answers", "total_questions", "passed", "completed_at")
    list_filter = ("passed", "quiz__subject", "completed_at")
    search_fields = ("user__email", "quiz__title")
    readonly_fields = ("completed_at",)

    def score_display(self, obj):
        color = "green" if obj.passed else "red"
        return format_html('<span style="color:{};font-weight:bold">{:.1f}%</span>', color, obj.score)
    score_display.short_description = "Ball"
