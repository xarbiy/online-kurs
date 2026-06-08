import json
import logging
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods, require_POST
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.db.models import Avg, Count

from .forms import (
    RegisterForm, LoginForm, ProfileForm,
    TelegramRegisterForm, TelegramLoginForm, OTPVerifyForm,
)
from .models import User, TelegramOTP
from .telegram_bot import send_otp_code, send_login_otp, send_welcome_message, get_bot_link
from quizzes.models import QuizResult
from courses.models import Course, Enrollment, Subject

logger = logging.getLogger(__name__)


# ─── Bosh sahifa ───────────────────────────────────────────────────────────────
def home(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    context = {
        "total_courses": Course.objects.filter(is_active=True).count(),
        "total_users": User.objects.filter(is_active=True).count(),
        "subjects_list": Subject.objects.all().order_by("order"),
    }
    return render(request, "home.html", context)


# ─── Email ro'yxatdan o'tish ──────────────────────────────────────────────────
@require_http_methods(["GET", "POST"])
def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            messages.success(request, f"Xush kelibsiz, {user.get_short_name()}! Muvaffaqiyatli ro'yxatdan o'tdingiz.")
            return redirect("dashboard")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})


# ─── Email login ──────────────────────────────────────────────────────────────
@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data["user"]
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            next_url = request.GET.get("next") or "dashboard"
            messages.success(request, f"Xush kelibsiz, {user.get_short_name()}!")
            return redirect(next_url)
    else:
        form = LoginForm()
    return render(request, "accounts/login.html", {"form": form})


# ─── Logout ───────────────────────────────────────────────────────────────────
@require_POST
def logout_view(request):
    logout(request)
    messages.info(request, "Tizimdan muvaffaqiyatli chiqdingiz.")
    return redirect("home")


# ─── Telegram: 1-qadam — ro'yxatdan o'tish ma'lumotlarini to'ldirish ──────────
@require_http_methods(["GET", "POST"])
def telegram_register_start(request):
    """
    Foydalanuvchi ism, email, parol yozadi.
    Keyin Telegram bot havolasiga yo'naltiriladi.
    """
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        form = TelegramRegisterForm(request.POST)
        if form.is_valid():
            # Ma'lumotlarni sessionda saqlash
            request.session["tg_reg_name"] = form.cleaned_data["name"]
            request.session["tg_reg_email"] = form.cleaned_data["email"]
            request.session["tg_reg_password"] = form.cleaned_data["password1"]
            request.session.modified = True
            return redirect("telegram_register_bot")
    else:
        form = TelegramRegisterForm()
    return render(request, "accounts/telegram_register.html", {"form": form})


# ─── Telegram: 2-qadam — bot havolasi ─────────────────────────────────────────
def telegram_register_bot(request):
    """Bot havolasini ko'rsatish sahifasi."""
    if request.user.is_authenticated:
        return redirect("dashboard")
    if not request.session.get("tg_reg_email"):
        return redirect("telegram_register_start")
    bot_link = get_bot_link("register")
    return render(request, "accounts/telegram_bot_redirect.html", {
        "bot_link": bot_link,
        "bot_username": settings.TELEGRAM_BOT_USERNAME,
        "step": "register",
    })


# ─── Telegram webhook: bot xabarlarini qabul qilish ──────────────────────────
def telegram_webhook(request):
    """
    Telegram bot webhook endpointi.
    Bot /contact xabarini qabul qiladi va OTP yuboradi.
    """
    if request.method != "POST":
        return JsonResponse({"ok": True})

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"ok": False}, status=400)

    message = data.get("message", {})
    contact = message.get("contact")
    chat = message.get("chat", {})
    chat_id = chat.get("id")
    from_user = message.get("from", {})
    text = message.get("text", "")

    if not chat_id:
        return JsonResponse({"ok": True})

    # /start buyrug'i
    if text.startswith("/start"):
        from .telegram_bot import send_telegram_message, request_contact_keyboard
        send_telegram_message(
            chat_id,
            "👋 <b>Akademiya botiga xush kelibsiz!</b>\n\n"
            "📱 Telefon raqamingizni tasdiqlash uchun quyidagi tugmani bosing:",
            reply_markup=request_contact_keyboard(),
        )
        return JsonResponse({"ok": True})

    # Telefon raqam kontakti
    if contact:
        phone_number = contact.get("phone_number", "")
        if not phone_number.startswith("+"):
            phone_number = "+" + phone_number

        telegram_id = from_user.get("id", chat_id)
        telegram_username = from_user.get("username", "")
        telegram_name = from_user.get("first_name", "")
        if from_user.get("last_name"):
            telegram_name += " " + from_user["last_name"]

        # Eski OTP larni o'chirish
        TelegramOTP.objects.filter(
            phone_number=phone_number, is_used=False
        ).update(is_used=True)

        # Yangi OTP yaratish
        code = TelegramOTP.generate_code()
        expires_at = timezone.now() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)

        otp = TelegramOTP.objects.create(
            phone_number=phone_number,
            telegram_id=telegram_id,
            telegram_username=telegram_username,
            telegram_name=telegram_name,
            code=code,
            expires_at=expires_at,
        )

        # OTP kodni yuborish
        sent = send_otp_code(chat_id, code, telegram_name)

        from .telegram_bot import send_telegram_message, remove_keyboard
        if sent:
            send_telegram_message(
                chat_id,
                f"✅ OTP kod yuborildi!\n\nKodni saytga kiriting: <b>{code}</b>\n\n"
                f"⏱ Kod <b>{settings.OTP_EXPIRE_MINUTES} daqiqa</b> ichida amal qiladi.",
                reply_markup=remove_keyboard(),
            )
        else:
            send_telegram_message(
                chat_id,
                "❌ Xatolik yuz berdi. Iltimos qayta urinib ko'ring.",
                reply_markup=remove_keyboard(),
            )

    return JsonResponse({"ok": True})


# ─── Telegram: 3-qadam — OTP kiritish (ro'yxatdan o'tish) ────────────────────
@require_http_methods(["GET", "POST"])
def telegram_register_verify(request):
    """OTP kodni tasdiqlash va hisob yaratish."""
    if request.user.is_authenticated:
        return redirect("dashboard")

    pending_name = request.session.get("tg_reg_name")
    pending_email = request.session.get("tg_reg_email")
    pending_password = request.session.get("tg_reg_password")

    if not pending_email:
        messages.error(request, "Sessiya muddati tugadi. Qaytadan boshlang.")
        return redirect("telegram_register_start")

    if request.method == "POST":
        form = OTPVerifyForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"]

            otp = TelegramOTP.objects.filter(
                code=code, is_used=False
            ).order_by("-created_at").first()

            if not otp:
                messages.error(request, "Noto'g'ri kod. Qaytadan urinib ko'ring.")
                return render(request, "accounts/otp_verify.html", {"form": form, "step": "register"})

            if otp.is_expired():
                messages.error(request, "Kod muddati tugagan. Qaytadan boshlang.")
                return redirect("telegram_register_bot")

            # Telefon raqam boshqa akkauntda band emasligini tekshirish
            if User.objects.filter(phone_number=otp.phone_number).exists():
                messages.error(request, "Bu telefon raqam bilan hisob allaqachon mavjud.")
                return redirect("login")

            # Email tekshirish
            if User.objects.filter(email=pending_email).exists():
                messages.error(request, "Bu email allaqachon ro'yxatdan o'tgan.")
                otp.is_used = True
                otp.save()
                for key in ("tg_reg_name", "tg_reg_email", "tg_reg_password"):
                    request.session.pop(key, None)
                return redirect("register")

            # Foydalanuvchi yaratish
            user = User.objects.create_user(
                email=pending_email,
                password=pending_password,
                name=pending_name or otp.telegram_name or "Foydalanuvchi",
                phone_number=otp.phone_number,
                telegram_id=otp.telegram_id,
                telegram_username=otp.telegram_username,
                is_telegram_verified=True,
                auth_method=User.AUTH_METHOD_TELEGRAM,
            )

            otp.is_used = True
            otp.save()

            # Session tozalash
            for key in ("tg_reg_name", "tg_reg_email", "tg_reg_password"):
                request.session.pop(key, None)

            # Xush kelibsiz xabari yuborish
            send_welcome_message(otp.telegram_id, user.get_short_name())

            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            messages.success(request, f"Tabriklaymiz, {user.get_short_name()}! Muvaffaqiyatli ro'yxatdan o'tdingiz. 🎉")
            return redirect("dashboard")
    else:
        form = OTPVerifyForm()

    return render(request, "accounts/otp_verify.html", {
        "form": form,
        "step": "register",
        "bot_username": settings.TELEGRAM_BOT_USERNAME,
    })


# ─── Telegram: Login — mavjud hisob bilan kirish ─────────────────────────────
@require_http_methods(["GET", "POST"])
def telegram_login_view(request):
    """Telegram orqali tizimga kirish."""
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        form = TelegramLoginForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data["phone_number"]
            user = User.objects.filter(phone_number=phone, is_telegram_verified=True).first()
            if not user:
                messages.error(request, "Bu telefon raqam bilan hisob topilmadi. Avval ro'yxatdan o'ting.")
                return render(request, "accounts/telegram_login.html", {"form": form})
            if not user.telegram_id:
                messages.error(request, "Bu hisob Telegram bilan bog'lanmagan.")
                return render(request, "accounts/telegram_login.html", {"form": form})

            # Eski OTP larni bekor qilish
            TelegramOTP.objects.filter(
                phone_number=phone, is_used=False
            ).update(is_used=True)

            # Yangi OTP yaratish
            code = TelegramOTP.generate_code()
            expires_at = timezone.now() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
            TelegramOTP.objects.create(
                phone_number=phone,
                telegram_id=user.telegram_id,
                telegram_username=user.telegram_username,
                telegram_name=user.name,
                code=code,
                expires_at=expires_at,
            )

            sent = send_login_otp(user.telegram_id, code, user.get_short_name())
            if sent:
                request.session["tg_login_phone"] = phone
                messages.info(request, f"OTP kod Telegram'ga yuborildi. {settings.OTP_EXPIRE_MINUTES} daqiqa ichida kiriting.")
                return redirect("telegram_login_verify")
            else:
                messages.error(request, "Telegram xabari yuborilmadi. Keyinroq urinib ko'ring.")
    else:
        form = TelegramLoginForm()
    return render(request, "accounts/telegram_login.html", {"form": form})


# ─── Telegram Login OTP verify ────────────────────────────────────────────────
@require_http_methods(["GET", "POST"])
def telegram_login_verify(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    phone = request.session.get("tg_login_phone")
    if not phone:
        return redirect("telegram_login")

    if request.method == "POST":
        form = OTPVerifyForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"]
            otp = TelegramOTP.objects.filter(
                phone_number=phone, code=code, is_used=False
            ).order_by("-created_at").first()

            if not otp:
                messages.error(request, "Noto'g'ri kod.")
                return render(request, "accounts/otp_verify.html", {"form": form, "step": "login"})

            if otp.is_expired():
                messages.error(request, "Kod muddati tugagan. Qaytadan urinib ko'ring.")
                return redirect("telegram_login")

            user = User.objects.filter(phone_number=phone).first()
            if not user:
                messages.error(request, "Foydalanuvchi topilmadi.")
                return redirect("telegram_login")

            otp.is_used = True
            otp.save()
            request.session.pop("tg_login_phone", None)

            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            messages.success(request, f"Xush kelibsiz, {user.get_short_name()}!")
            return redirect(request.GET.get("next") or "dashboard")
    else:
        form = OTPVerifyForm()

    return render(request, "accounts/otp_verify.html", {
        "form": form,
        "step": "login",
        "bot_username": settings.TELEGRAM_BOT_USERNAME,
    })


# ─── Dashboard ────────────────────────────────────────────────────────────────
@login_required
def dashboard_view(request):
    user = request.user
    enrollments = Enrollment.objects.filter(user=user).select_related("course")
    recent_results = QuizResult.objects.filter(user=user).select_related("quiz").order_by("-completed_at")[:5]
    total_results = QuizResult.objects.filter(user=user)
    agg = total_results.aggregate(avg=Avg("score"), count=Count("id"))
    avg_score = round(agg["avg"] or 0, 1)
    total_quiz_count = agg["count"]

    context = {
        "enrollments": enrollments,
        "recent_results": recent_results,
        "total_quizzes": total_quiz_count,
        "avg_score": avg_score,
        "enrolled_count": enrollments.count(),
    }
    return render(request, "dashboard.html", context)


# ─── Profil ───────────────────────────────────────────────────────────────────
@login_required
def profile_view(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil muvaffaqiyatli yangilandi.")
            return redirect("profile")
    else:
        form = ProfileForm(instance=request.user)
    return render(request, "accounts/profile.html", {"form": form})
