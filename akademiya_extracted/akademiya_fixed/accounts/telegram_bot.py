"""
Akademiya — Telegram Bot
========================
Bu fayl Django loyihasida Telegram bot orqali OTP yuborish uchun ishlatiladi.

Bot sozlash tartibi:
  1. @BotFather ga yozing va /newbot buyrug'ini bajaring
  2. Bot nomini va username'ini kiriting
  3. Olingan tokenni .env fayliga yozing: TELEGRAM_BOT_TOKEN=...
  4. Bot username'ini yozing: TELEGRAM_BOT_USERNAME=YourBotUsername
  5. Webhook o'rnatish (server deploy qilingandan so'ng):
     https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://sizning-domen.uz/accounts/telegram/webhook/

Lokal test uchun ngrok ishlatish mumkin:
  ngrok http 8000
  Keyin webhook URL: https://xxxx.ngrok.io/accounts/telegram/webhook/
"""

import json
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

TELEGRAM_API_BASE = "https://api.telegram.org/bot{token}/{method}"


# ─── Asosiy yuboruvchi funksiya ───────────────────────────────────────────────

def _call(method: str, payload: dict) -> dict:
    """Telegram API ga so'rov yuborish."""
    token = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
    if not token:
        logger.warning("TELEGRAM_BOT_TOKEN sozlanmagan — bot ishlamaydi")
        return {"ok": False}
    url = TELEGRAM_API_BASE.format(token=token, method=method)
    try:
        resp = requests.post(url, json=payload, timeout=10)
        return resp.json()
    except requests.RequestException as e:
        logger.error(f"Telegram API xatosi ({method}): {e}")
        return {"ok": False}


def send_telegram_message(chat_id: int, text: str, reply_markup=None) -> bool:
    """Foydalanuvchiga oddiy xabar yuborish."""
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    result = _call("sendMessage", payload)
    return result.get("ok", False)


# ─── Klaviaturalar ────────────────────────────────────────────────────────────

def request_contact_keyboard() -> dict:
    """Telefon raqam so'rash klaviaturasi."""
    return {
        "keyboard": [[
            {
                "text": "📱 Telefon raqamimni yuborish",
                "request_contact": True
            }
        ]],
        "resize_keyboard": True,
        "one_time_keyboard": True,
    }


def remove_keyboard() -> dict:
    """Klaviaturani olib tashlash."""
    return {"remove_keyboard": True}


# ─── OTP xabarlari ───────────────────────────────────────────────────────────

def send_otp_code(telegram_id: int, code: str, name: str = "") -> bool:
    """Ro'yxatdan o'tish uchun OTP kod yuborish."""
    greeting = f"Assalomu alaykum, <b>{name}</b>!" if name else "Assalomu alaykum!"
    expire = getattr(settings, "OTP_EXPIRE_MINUTES", 5)
    text = (
        f"🎓 <b>Akademiya — Tasdiqlash kodi</b>\n\n"
        f"{greeting}\n\n"
        f"Ro'yxatdan o'tish uchun tasdiqlash kodingiz:\n\n"
        f"<b>┌─────────────────┐</b>\n"
        f"<b>│   {code}   │</b>\n"
        f"<b>└─────────────────┘</b>\n\n"
        f"⏱ Kod <b>{expire} daqiqa</b> ichida amal qiladi\n"
        f"⚠️ Kodni hech kimga bermang!"
    )
    return send_telegram_message(telegram_id, text)


def send_login_otp(telegram_id: int, code: str, name: str = "") -> bool:
    """Kirish uchun OTP kod yuborish."""
    greeting = f"Xush kelibsiz, <b>{name}</b>!" if name else "Xush kelibsiz!"
    expire = getattr(settings, "OTP_EXPIRE_MINUTES", 5)
    text = (
        f"🔑 <b>Akademiya — Kirish kodi</b>\n\n"
        f"{greeting}\n\n"
        f"Tizimga kirish uchun kodingiz:\n\n"
        f"<b>┌─────────────────┐</b>\n"
        f"<b>│   {code}   │</b>\n"
        f"<b>└─────────────────┘</b>\n\n"
        f"⏱ Kod <b>{expire} daqiqa</b> ichida amal qiladi\n"
        f"🚫 Agar siz so'rov yubormagan bo'lsangiz, bu xabarni e'tiborsiz qoldiring"
    )
    return send_telegram_message(telegram_id, text)


def send_welcome_message(telegram_id: int, name: str) -> bool:
    """Muvaffaqiyatli ro'yxatdan o'tgandan keyin xush kelibsiz."""
    site_url = "http://127.0.0.1:8000"
    text = (
        f"🎉 <b>Tabriklaymiz, {name}!</b>\n\n"
        f"Siz <b>Akademiya</b> platformasiga muvaffaqiyatli ro'yxatdan o'tdingiz!\n\n"
        f"📚 <b>Nima bor?</b>\n"
        f"• 📖 Interaktiv kurslar\n"
        f"• ✅ Test sinovlari\n"
        f"• 💻 Kod muharriri (Python, JS, Java...)\n"
        f"• 🏆 Reyting va sertifikatlar\n"
        f"• 💬 Qo'llab-quvvatlash xizmati\n\n"
        f"👉 Saytga o'ting va o'qishni boshlang!"
    )
    return send_telegram_message(telegram_id, text)


# ─── Bot havolasi ─────────────────────────────────────────────────────────────

def get_bot_link(payload: str = "") -> str:
    """Bot deep link havolasi."""
    username = getattr(settings, "TELEGRAM_BOT_USERNAME", "AkademiyaBot")
    if payload:
        return f"https://t.me/{username}?start={payload}"
    return f"https://t.me/{username}"


# ─── Webhook o'rnatish (deploy qilingandan keyin chaqiriladi) ─────────────────

def set_webhook(webhook_url: str) -> bool:
    """Telegram webhook URL ni o'rnatish."""
    result = _call("setWebhook", {"url": webhook_url})
    if result.get("ok"):
        logger.info(f"Webhook o'rnatildi: {webhook_url}")
        return True
    logger.error(f"Webhook o'rnatilmadi: {result}")
    return False


def delete_webhook() -> bool:
    """Webhookni o'chirish (polling uchun)."""
    result = _call("deleteWebhook", {})
    return result.get("ok", False)


def get_bot_info() -> dict:
    """Bot ma'lumotlarini olish."""
    return _call("getMe", {})
