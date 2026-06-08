import random
import string
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email majburiy")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser is_staff=True bo'lishi kerak")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser is_superuser=True bo'lishi kerak")
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name="Email")
    name = models.CharField(max_length=150, verbose_name="To'liq ism")
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True, verbose_name="Avatar")
    bio = models.TextField(blank=True, verbose_name="Bio")

    # Telegram autentifikatsiya
    phone_number = models.CharField(
        max_length=20, blank=True, null=True, unique=True,
        verbose_name="Telefon raqam",
        help_text="+998901234567 formatida"
    )
    telegram_id = models.BigIntegerField(
        null=True, blank=True, unique=True,
        verbose_name="Telegram ID"
    )
    telegram_username = models.CharField(
        max_length=100, blank=True, verbose_name="Telegram username"
    )
    is_telegram_verified = models.BooleanField(
        default=False, verbose_name="Telegram tasdiqlangan"
    )

    # Auth method
    AUTH_METHOD_EMAIL = "email"
    AUTH_METHOD_GOOGLE = "google"
    AUTH_METHOD_TELEGRAM = "telegram"
    AUTH_METHOD_CHOICES = [
        (AUTH_METHOD_EMAIL, "Email"),
        (AUTH_METHOD_GOOGLE, "Google"),
        (AUTH_METHOD_TELEGRAM, "Telegram"),
    ]
    auth_method = models.CharField(
        max_length=20, choices=AUTH_METHOD_CHOICES,
        default=AUTH_METHOD_EMAIL, verbose_name="Ro'yxatdan o'tish usuli"
    )

    is_active = models.BooleanField(default=True, verbose_name="Faol")
    is_staff = models.BooleanField(default=False, verbose_name="Xodim")
    date_joined = models.DateTimeField(default=timezone.now, verbose_name="Ro'yxatdan o'tgan sana")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    objects = UserManager()

    class Meta:
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"
        ordering = ["-date_joined"]

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name.split()[0] if self.name else self.email.split("@")[0]

    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return None


class TelegramOTP(models.Model):
    """Telegram orqali ro'yxatdan o'tish uchun OTP kodlari"""
    phone_number = models.CharField(max_length=20, verbose_name="Telefon raqam")
    telegram_id = models.BigIntegerField(verbose_name="Telegram ID")
    telegram_username = models.CharField(max_length=100, blank=True, verbose_name="Telegram username")
    telegram_name = models.CharField(max_length=150, blank=True, verbose_name="Telegram ismi")
    code = models.CharField(max_length=6, verbose_name="OTP kod")
    is_used = models.BooleanField(default=False, verbose_name="Ishlatilgan")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan")
    expires_at = models.DateTimeField(verbose_name="Tugash vaqti")

    # Ro'yxatdan o'tish uchun qo'shimcha ma'lumotlar
    pending_name = models.CharField(max_length=150, blank=True, verbose_name="Ism (kutilmoqda)")
    pending_email = models.EmailField(blank=True, verbose_name="Email (kutilmoqda)")
    pending_password = models.CharField(max_length=255, blank=True, verbose_name="Parol hash (kutilmoqda)")

    class Meta:
        verbose_name = "Telegram OTP"
        verbose_name_plural = "Telegram OTP kodlari"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.phone_number} - {self.code}"

    @staticmethod
    def generate_code():
        return "".join(random.choices(string.digits, k=6))

    def is_expired(self):
        return timezone.now() > self.expires_at

    def is_valid(self):
        return not self.is_used and not self.is_expired()
