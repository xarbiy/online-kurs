from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Subject, Course, Lesson, Enrollment, LessonProgress


def course_list(request):
    subjects = Subject.objects.prefetch_related("courses").all()
    subject_filter = request.GET.get("subject", "")
    if subject_filter:
        courses = Course.objects.filter(subject__slug=subject_filter, is_active=True).select_related("subject")
    else:
        courses = Course.objects.filter(is_active=True).select_related("subject")

    enrollments = set()
    if request.user.is_authenticated:
        enrollments = set(Enrollment.objects.filter(user=request.user).values_list("course_id", flat=True))

    return render(request, "courses/list.html", {
        "courses": courses,
        "subjects": subjects,
        "enrollments": enrollments,
        "subject_filter": subject_filter,
    })


def course_detail(request, subject_slug, course_slug):
    course = get_object_or_404(Course, subject__slug=subject_slug, slug=course_slug, is_active=True)
    lessons = course.lessons.all()
    is_enrolled = False
    completed_lessons = set()

    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
        completed_lessons = set(
            LessonProgress.objects.filter(user=request.user, lesson__course=course, completed=True)
            .values_list("lesson_id", flat=True)
        )

    return render(request, "courses/detail.html", {
        "course": course,
        "lessons": lessons,
        "is_enrolled": is_enrolled,
        "completed_lessons": completed_lessons,
    })


@login_required
def enroll_course(request, subject_slug, course_slug):
    course = get_object_or_404(Course, subject__slug=subject_slug, slug=course_slug, is_active=True)
    enrollment, created = Enrollment.objects.get_or_create(user=request.user, course=course)
    if created:
        messages.success(request, f"'{course.title}' kursiga muvaffaqiyatli yozildingiz!")
    else:
        messages.info(request, "Siz bu kursga allaqachon yozilgansiz.")
    return redirect("course_detail", subject_slug=subject_slug, course_slug=course_slug)


@login_required
def lesson_view(request, subject_slug, course_slug, lesson_id):
    course = get_object_or_404(Course, subject__slug=subject_slug, slug=course_slug)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)

    if not Enrollment.objects.filter(user=request.user, course=course).exists():
        messages.warning(request, "Bu kursni ko'rish uchun avval yoziling.")
        return redirect("course_detail", subject_slug=subject_slug, course_slug=course_slug)

    if request.method == "POST" and request.POST.get("mark_complete"):
        progress, _ = LessonProgress.objects.get_or_create(user=request.user, lesson=lesson)
        if not progress.completed:
            progress.completed = True
            progress.completed_at = timezone.now()
            progress.save()
            messages.success(request, "Dars tugatildi deb belgilandi!")

    progress = LessonProgress.objects.filter(user=request.user, lesson=lesson).first()
    lessons = list(course.lessons.all())
    current_index = next((i for i, l in enumerate(lessons) if l.id == lesson.id), 0)
    next_lesson = lessons[current_index + 1] if current_index + 1 < len(lessons) else None
    prev_lesson = lessons[current_index - 1] if current_index > 0 else None

    return render(request, "courses/lesson.html", {
        "course": course,
        "lesson": lesson,
        "progress": progress,
        "next_lesson": next_lesson,
        "prev_lesson": prev_lesson,
    })
