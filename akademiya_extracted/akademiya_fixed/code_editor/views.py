from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
import urllib.request
import urllib.error
from .models import CodeSubmission, CodeChallenge, LANGUAGE_CHOICES


# Piston API orqali kod ishlatish uchun tillar xaritasi
PISTON_LANGUAGE_MAP = {
    "python": ("python", "3.10.0"),
    "javascript": ("javascript", "18.15.0"),
    "java": ("java", "15.0.2"),
    "cpp": ("cpp", "10.2.0"),
    "c": ("c", "10.2.0"),
    "sql": None,   # SQL execution qo'llab-quvvatlanmaydi
    "html": None,  # HTML execution qo'llab-quvvatlanmaydi
    "css": None,   # CSS execution qo'llab-quvvatlanmaydi
}


@login_required
def editor_home(request):
    challenges = CodeChallenge.objects.filter(is_active=True)
    my_submissions = CodeSubmission.objects.filter(user=request.user).order_by("-updated_at")[:10]
    public_submissions = CodeSubmission.objects.filter(is_public=True).exclude(user=request.user).select_related("user").order_by("-created_at")[:10]

    return render(request, "code_editor/home.html", {
        "challenges": challenges,
        "my_submissions": my_submissions,
        "public_submissions": public_submissions,
        "languages": LANGUAGE_CHOICES,
    })


@login_required
def new_submission(request):
    challenge_id = request.GET.get("challenge")
    challenge = None
    starter_code = ""
    language = "python"

    if challenge_id:
        challenge = get_object_or_404(CodeChallenge, id=challenge_id, is_active=True)
        starter_code = challenge.starter_code
        language = challenge.language

    if request.method == "POST":
        title = request.POST.get("title", "Mening kodum")
        language = request.POST.get("language", "python")
        code = request.POST.get("code", "")
        is_public = request.POST.get("is_public") == "on"
        status = request.POST.get("status", "draft")

        submission = CodeSubmission.objects.create(
            user=request.user,
            challenge=challenge,
            title=title,
            language=language,
            code=code,
            is_public=is_public,
            status=status,
        )
        messages.success(request, "Kod muvaffaqiyatli saqlandi!")
        return redirect("view_submission", submission_id=submission.id)

    return render(request, "code_editor/editor.html", {
        "challenge": challenge,
        "starter_code": starter_code,
        "language": language,
        "languages": LANGUAGE_CHOICES,
        "submission": None,
    })


@login_required
def edit_submission(request, submission_id):
    submission = get_object_or_404(CodeSubmission, id=submission_id, user=request.user)

    if request.method == "POST":
        submission.title = request.POST.get("title", submission.title)
        submission.language = request.POST.get("language", submission.language)
        submission.code = request.POST.get("code", submission.code)
        submission.is_public = request.POST.get("is_public") == "on"
        submission.status = request.POST.get("status", submission.status)
        submission.save()
        messages.success(request, "Kod yangilandi!")
        return redirect("view_submission", submission_id=submission.id)

    return render(request, "code_editor/editor.html", {
        "submission": submission,
        "language": submission.language,
        "languages": LANGUAGE_CHOICES,
        "challenge": submission.challenge,
    })


@login_required
def view_submission(request, submission_id):
    submission = get_object_or_404(CodeSubmission, id=submission_id)
    if not submission.is_public and submission.user != request.user:
        messages.error(request, "Bu kod ommaviy emas.")
        return redirect("editor_home")
    return render(request, "code_editor/view.html", {"submission": submission})


@login_required
def delete_submission(request, submission_id):
    submission = get_object_or_404(CodeSubmission, id=submission_id, user=request.user)
    submission.delete()
    messages.success(request, "Kod o'chirildi.")
    return redirect("editor_home")


@login_required
def challenge_detail(request, challenge_id):
    challenge = get_object_or_404(CodeChallenge, id=challenge_id, is_active=True)
    my_submission = CodeSubmission.objects.filter(user=request.user, challenge=challenge).first()
    return render(request, "code_editor/challenge.html", {
        "challenge": challenge,
        "my_submission": my_submission,
        "languages": LANGUAGE_CHOICES,
    })


@login_required
@require_POST
def run_code(request):
    """Kodni Piston API orqali ishlatadi va natijani JSON formatida qaytaradi."""
    try:
        data = json.loads(request.body)
        code = data.get("code", "").strip()
        language = data.get("language", "python")
        stdin = data.get("stdin", "")
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({"error": "Noto'g'ri so'rov formati."}, status=400)

    if not code:
        return JsonResponse({"error": "Kod bo'sh bo'lishi mumkin emas."}, status=400)

    piston_info = PISTON_LANGUAGE_MAP.get(language)
    if piston_info is None:
        return JsonResponse({
            "output": "",
            "error": f"'{language}' tili uchun kod ishlatish qo'llab-quvvatlanmaydi.",
            "run": False,
        })

    piston_lang, piston_version = piston_info
    payload = json.dumps({
        "language": piston_lang,
        "version": piston_version,
        "files": [{"name": "main", "content": code}],
        "stdin": stdin,
        "args": [],
        "compile_timeout": 10000,
        "run_timeout": 5000,
    }).encode("utf-8")

    try:
        req = urllib.request.Request(
            "https://emkc.org/api/v2/piston/execute",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode("utf-8"))

        run = result.get("run", {})
        compile_info = result.get("compile", {})

        output = run.get("stdout", "")
        stderr = run.get("stderr", "")
        compile_err = compile_info.get("stderr", "") if compile_info else ""

        return JsonResponse({
            "output": output,
            "stderr": stderr or compile_err,
            "exit_code": run.get("code", 0),
            "run": True,
        })

    except urllib.error.URLError as e:
        return JsonResponse({
            "error": f"Tashqi API bilan bog'lanishda xatolik: {str(e)}",
            "run": False,
        }, status=502)
    except Exception as e:
        return JsonResponse({
            "error": f"Kutilmagan xatolik: {str(e)}",
            "run": False,
        }, status=500)
