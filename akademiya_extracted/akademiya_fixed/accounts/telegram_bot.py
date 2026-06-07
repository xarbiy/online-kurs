"""
Telegram bot OTP xizmati.
Bot foydalanuvchiga OTP kod yuboradi va telefon raqamini tasdiqlaydi.

Ishlatish tartibi:
  1. Foydalanuvchi saytda ro'yxatdan o'tish formasini to'ldiradi (ism, email, parol)
  2. "Telegram orqali tasdiqlash" tugmasini bosadi
  3. Bot havolasiga o'tadi va /start bosadi
  4. Bot telefon raqam so'raydi (Telegram "Contact yuborish" tugmasi)
  5. Bot 6 xonali OTP kodni yuboradi
  6. Foydalanuvchi OTP ni saytga kiritadi → ro'yxatdan o'tish tugaydi
"""

import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

TELEGRAM_API = "https://api.telegram.org/bot{token}/{method}"


def send_telegram_message(chat_id: int, text: str, reply_markup=None) -> bool:
    """Telegram foydalanuvchisiga xabar yuborish."""
    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        logger.warning("TELEGRAM_BOT_TOKEN sozlanmagan")
        return False

    url = TELEGRAM_API.format(token=token, method="sendMessage")
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup

    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        return True
    except requests.RequestException as e:
        logger.error(f"Telegram xabar yuborishda xato: {e}")
        return False


def send_otp_code(telegram_id: int, code: str, name: str = "") -> bool:
    """OTP kodni Telegram orqali yuborish."""
    greeting = f"Salom, {name}! " if name else "Salom! "
    text = (
        f"🔐 <b>Akademiya — Tasdiqlash kodi</b>\n\n"
        f"{greeting}\n"
        f"Saytga ro'yxatdan o'tish uchun quyidagi kodni kiriting:\n\n"
        f"<code>{code}</code>\n\n"
        f"⏱ Kod <b>5 daqiqa</b> ichida amal qiladi.\n"
        f"⚠️ Agar siz so'rov yubormagan bo'lsangiz, ushbu xabarni e'tiborsiz qoldiring."
    )
    return send_telegram_message(telegram_id, text)


def send_login_otp(telegram_id: int, code: str, name: str = "") -> bool:
    """Login uchun OTP kodni Telegram orqali yuborish."""
    greeting = f"Salom, {name}! " if name else "Salom! "
    text = (
        f"🔑 <b>Akademiya — Kirish kodi</b>\n\n"
        f"{greeting}\n"
        f"Tizimga kirish uchun quyidagi kodni kiriting:\n\n"
        f"<code>{code}</code>\n\n"
        f"⏱ Kod <b>5 daqiqa</b> ichida amal qiladi.\n"
        f"⚠️ Agar siz so'rov yubormagan bo'lsangiz, parolingizni o'zgartiring!"
    )
    return send_telegram_message(telegram_id, text)


def send_welcome_message(telegram_id: int, name: str) -> bool:
    """Ro'yxatdan o'tgandan keyin xush kelibsiz xabari."""
    text = (
        f"🎉 <b>Tabriklaymiz, {name}!</b>\n\n"
        f"Siz Akademiya platformasiga muvaffaqiyatli ro'yxatdan o'tdingiz.\n\n"
        f"🌐 Saytga o'tish: <a href='https://akademiya.uz'>akademiya.uz</a>\n\n"
        f"📚 Kurslar, testlar va kod muharriri sizni kutmoqda!"
    )
    return send_telegram_message(telegram_id, text)


def get_bot_link(payload: str = "") -> str:
    """Bot havolasini qaytaradi (deep link bilan)."""
    username = settings.TELEGRAM_BOT_USERNAME
    if payload:
        return f"https://t.me/{username}?start={payload}"
    return f"https://t.me/{username}"


def request_contact_keyboard() -> dict:
    """Telefon raqam yuborish uchun Telegram klaviaturasi."""
    return {
        "keyboard": [
            [{"text": "📱 Telefon raqamni yuborish", "request_contact": True}]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": True,
    }


def remove_keyboard() -> dict:
    """Klaviaturani olib tashlash."""
    return {"remove_keyboard": True}
