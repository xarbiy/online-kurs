from django.db import models
from django.conf import settings


class SupportTicket(models.Model):
    STATUS_OPEN = "open"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_RESOLVED = "resolved"
    STATUS_CLOSED = "closed"
    STATUS_CHOICES = [
        (STATUS_OPEN,        "Ochiq"),
        (STATUS_IN_PROGRESS, "Ko'rib chiqilmoqda"),
        (STATUS_RESOLVED,    "Hal qilindi"),
        (STATUS_CLOSED,      "Yopildi"),
    ]

    PRIORITY_LOW = "low"
    PRIORITY_MEDIUM = "medium"
    PRIORITY_HIGH = "high"
    PRIORITY_CHOICES = [
        (PRIORITY_LOW,    "Past"),
        (PRIORITY_MEDIUM, "O'rta"),
        (PRIORITY_HIGH,   "Yuqori"),
    ]

    CATEGORY_CHOICES = [
        ("technical",  "Texnik muammo"),
        ("account",    "Hisob muammosi"),
        ("course",     "Kurs bo'yicha savol"),
        ("payment",    "To'lov"),
        ("suggestion", "Taklif"),
        ("other",      "Boshqa"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="support_tickets",
        verbose_name="Foydalanuvchi",
    )
    ticket_number = models.CharField(max_length=20, unique=True, verbose_name="Ticket raqami")
    subject = models.CharField(max_length=200, verbose_name="Mavzu")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="other", verbose_name="Kategoriya")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM, verbose_name="Ustuvorlik")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN, verbose_name="Holat")
    message = models.TextField(verbose_name="Xabar")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan")
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name="Hal qilingan vaqt")

    class Meta:
        verbose_name = "Support ticket"
        verbose_name_plural = "Support ticketlar"
        ordering = ["-created_at"]

    def __str__(self):
        return f"#{self.ticket_number} — {self.subject}"

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            self.ticket_number = self._generate_ticket_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_ticket_number():
        import random
        import string
        from django.utils import timezone
        prefix = timezone.now().strftime("%Y%m")
        suffix = "".join(random.choices(string.digits + string.ascii_uppercase, k=4))
        return f"AK-{prefix}-{suffix}"

    @property
    def status_color(self):
        colors = {
            self.STATUS_OPEN:        "warning",
            self.STATUS_IN_PROGRESS: "info",
            self.STATUS_RESOLVED:    "success",
            self.STATUS_CLOSED:      "secondary",
        }
        return colors.get(self.status, "secondary")

    @property
    def priority_color(self):
        colors = {
            self.PRIORITY_LOW:    "success",
            self.PRIORITY_MEDIUM: "warning",
            self.PRIORITY_HIGH:   "danger",
        }
        return colors.get(self.priority, "secondary")


class TicketReply(models.Model):
    ticket = models.ForeignKey(
        SupportTicket,
        on_delete=models.CASCADE,
        related_name="replies",
        verbose_name="Ticket",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ticket_replies",
        verbose_name="Foydalanuvchi",
    )
    message = models.TextField(verbose_name="Javob")
    is_staff_reply = models.BooleanField(default=False, verbose_name="Admin javobi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan")

    class Meta:
        verbose_name = "Ticket javobi"
        verbose_name_plural = "Ticket javoblari"
        ordering = ["created_at"]

    def __str__(self):
        role = "Admin" if self.is_staff_reply else self.user.get_short_name()
        return f"{role} → #{self.ticket.ticket_number}"
