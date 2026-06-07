from django.db import models
from django.conf import settings


LANGUAGE_CHOICES = [
    ("python", "Python"),
    ("javascript", "JavaScript"),
    ("java", "Java"),
    ("cpp", "C++"),
    ("c", "C"),
    ("sql", "SQL"),
    ("html", "HTML"),
    ("css", "CSS"),
]


class CodeChallenge(models.Model):
    title = models.CharField(max_length=200, verbose_name="Sarlavha")
    description = models.TextField(verbose_name="Tavsif")
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, default="python", verbose_name="Til")
    starter_code = models.TextField(blank=True, verbose_name="Boshlang'ich kod")
    solution_code = models.TextField(blank=True, verbose_name="Yechim kodi")
    difficulty = models.CharField(max_length=20, choices=[("easy", "Oson"), ("medium", "O'rta"), ("hard", "Qiyin")], default="easy", verbose_name="Qiyinlik")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan")

    class Meta:
        verbose_name = "Kod topshirig'i"
        verbose_name_plural = "Kod topshiriqlari"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class CodeSubmission(models.Model):
    STATUS_CHOICES = [
        ("draft", "Qoralama"),
        ("submitted", "Topshirildi"),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="code_submissions", verbose_name="Foydalanuvchi")
    challenge = models.ForeignKey(CodeChallenge, on_delete=models.SET_NULL, null=True, blank=True, related_name="submissions", verbose_name="Topshiriq")
    title = models.CharField(max_length=200, default="Mening kodum", verbose_name="Sarlavha")
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, default="python", verbose_name="Dasturlash tili")
    code = models.TextField(verbose_name="Kod")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft", verbose_name="Holat")
    is_public = models.BooleanField(default=False, verbose_name="Ommaviy")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan")

    class Meta:
        verbose_name = "Kod topshirmasi"
        verbose_name_plural = "Kod topshirmalari"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} - {self.title}"
