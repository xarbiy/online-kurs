import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Quiz, Question, Answer, QuizAttempt, UserAnswer, QuizResult
from courses.models import Subject


@login_required
def quiz_list(request):
    subjects = Subject.objects.prefetch_related("quizzes").all()
    subject_filter = request.GET.get("subject", "")
    if subject_filter:
        quizzes = Quiz.objects.filter(subject__slug=subject_filter, is_active=True).select_related("subject")
    else:
        quizzes = Quiz.objects.filter(is_active=True).select_related("subject")

    user_results = {}
    for result in QuizResult.objects.filter(user=request.user).select_related("quiz"):
        if result.quiz_id not in user_results:
            user_results[result.quiz_id] = result

    return render(request, "quizzes/list.html", {
        "quizzes": quizzes,
        "subjects": subjects,
        "user_results": user_results,
        "subject_filter": subject_filter,
    })


@login_required
def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, is_active=True)
    past_results = QuizResult.objects.filter(user=request.user, quiz=quiz).order_by("-completed_at")[:5]
    best_result = past_results.order_by("-score").first() if past_results else None

    return render(request, "quizzes/detail.html", {
        "quiz": quiz,
        "past_results": past_results,
        "best_result": best_result,
    })


@login_required
def start_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, is_active=True)
    if not quiz.questions.exists():
        messages.error(request, "Bu testda hali savollar yo'q.")
        return redirect("quiz_detail", quiz_id=quiz_id)

    attempt = QuizAttempt.objects.create(user=request.user, quiz=quiz, status="in_progress")
    return redirect("take_quiz", attempt_id=attempt.id)


@login_required
def take_quiz(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user, status="in_progress")
    quiz = attempt.quiz
    questions = quiz.questions.prefetch_related("answers").all()

    if request.method == "POST":
        earned_points = 0
        total_points = 0
        correct = 0
        total = questions.count()

        for question in questions:
            total_points += question.points
            answer_id = request.POST.get(f"question_{question.id}")
            if answer_id:
                try:
                    answer = Answer.objects.get(id=answer_id, question=question)
                    UserAnswer.objects.update_or_create(
                        attempt=attempt, question=question,
                        defaults={"answer": answer},
                    )
                    if answer.is_correct:
                        correct += 1
                        earned_points += question.points
                except Answer.DoesNotExist:
                    pass

        score = (earned_points / total_points * 100) if total_points > 0 else 0
        passed = score >= quiz.pass_score

        attempt.status = "completed"
        attempt.completed_at = timezone.now()
        attempt.save()

        result = QuizResult.objects.create(
            user=request.user,
            quiz=quiz,
            attempt=attempt,
            score=score,
            correct_answers=correct,
            total_questions=total,
            passed=passed,
        )
        return redirect("quiz_result", result_id=result.id)

    return render(request, "quizzes/take.html", {
        "attempt": attempt,
        "quiz": quiz,
        "questions": questions,
        "time_limit_seconds": quiz.time_limit * 60,
    })


@login_required
def quiz_result(request, result_id):
    result = get_object_or_404(QuizResult, id=result_id, user=request.user)
    attempt = result.attempt
    questions_with_answers = []

    for question in attempt.quiz.questions.prefetch_related("answers"):
        user_answer = UserAnswer.objects.filter(attempt=attempt, question=question).first()
        correct_answer = question.answers.filter(is_correct=True).first()
        questions_with_answers.append({
            "question": question,
            "user_answer": user_answer.answer if user_answer else None,
            "correct_answer": correct_answer,
            "is_correct": user_answer and user_answer.answer and user_answer.answer.is_correct,
        })

    return render(request, "quizzes/result.html", {
        "result": result,
        "questions_with_answers": questions_with_answers,
    })


@login_required
def my_results(request):
    results = QuizResult.objects.filter(user=request.user).select_related("quiz", "quiz__subject").order_by("-completed_at")
    return render(request, "quizzes/my_results.html", {"results": results})
