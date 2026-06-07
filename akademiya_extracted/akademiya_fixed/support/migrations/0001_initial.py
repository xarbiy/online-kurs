import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="SupportTicket",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("ticket_number", models.CharField(max_length=20, unique=True, verbose_name="Ticket raqami")),
                ("subject", models.CharField(max_length=200, verbose_name="Mavzu")),
                ("category", models.CharField(
                    choices=[("technical","Texnik muammo"),("account","Hisob muammosi"),("course","Kurs bo'yicha savol"),("payment","To'lov"),("suggestion","Taklif"),("other","Boshqa")],
                    default="other", max_length=20, verbose_name="Kategoriya"
                )),
                ("priority", models.CharField(
                    choices=[("low","Past"),("medium","O'rta"),("high","Yuqori")],
                    default="medium", max_length=10, verbose_name="Ustuvorlik"
                )),
                ("status", models.CharField(
                    choices=[("open","Ochiq"),("in_progress","Ko'rib chiqilmoqda"),("resolved","Hal qilindi"),("closed","Yopildi")],
                    default="open", max_length=20, verbose_name="Holat"
                )),
                ("message", models.TextField(verbose_name="Xabar")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Yangilangan")),
                ("resolved_at", models.DateTimeField(blank=True, null=True, verbose_name="Hal qilingan vaqt")),
                ("user", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="support_tickets",
                    to=settings.AUTH_USER_MODEL,
                    verbose_name="Foydalanuvchi",
                )),
            ],
            options={
                "verbose_name": "Support ticket",
                "verbose_name_plural": "Support ticketlar",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="TicketReply",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("message", models.TextField(verbose_name="Javob")),
                ("is_staff_reply", models.BooleanField(default=False, verbose_name="Admin javobi")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan")),
                ("ticket", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="replies",
                    to="support.supportticket",
                    verbose_name="Ticket",
                )),
                ("user", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="ticket_replies",
                    to=settings.AUTH_USER_MODEL,
                    verbose_name="Foydalanuvchi",
                )),
            ],
            options={
                "verbose_name": "Ticket javobi",
                "verbose_name_plural": "Ticket javoblari",
                "ordering": ["created_at"],
            },
        ),
    ]
