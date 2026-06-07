import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="phone_number",
            field=models.CharField(
                blank=True, max_length=20, null=True, unique=True,
                verbose_name="Telefon raqam",
                help_text="+998901234567 formatida"
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="telegram_id",
            field=models.BigIntegerField(blank=True, null=True, unique=True, verbose_name="Telegram ID"),
        ),
        migrations.AddField(
            model_name="user",
            name="telegram_username",
            field=models.CharField(blank=True, max_length=100, verbose_name="Telegram username"),
        ),
        migrations.AddField(
            model_name="user",
            name="is_telegram_verified",
            field=models.BooleanField(default=False, verbose_name="Telegram tasdiqlangan"),
        ),
        migrations.AddField(
            model_name="user",
            name="auth_method",
            field=models.CharField(
                choices=[("email", "Email"), ("google", "Google"), ("telegram", "Telegram")],
                default="email", max_length=20, verbose_name="Ro'yxatdan o'tish usuli"
            ),
        ),
        migrations.CreateModel(
            name="TelegramOTP",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("phone_number", models.CharField(max_length=20, verbose_name="Telefon raqam")),
                ("telegram_id", models.BigIntegerField(verbose_name="Telegram ID")),
                ("telegram_username", models.CharField(blank=True, max_length=100, verbose_name="Telegram username")),
                ("telegram_name", models.CharField(blank=True, max_length=150, verbose_name="Telegram ismi")),
                ("code", models.CharField(max_length=6, verbose_name="OTP kod")),
                ("is_used", models.BooleanField(default=False, verbose_name="Ishlatilgan")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan")),
                ("expires_at", models.DateTimeField(verbose_name="Tugash vaqti")),
                ("pending_name", models.CharField(blank=True, max_length=150, verbose_name="Ism (kutilmoqda)")),
                ("pending_email", models.EmailField(blank=True, verbose_name="Email (kutilmoqda)")),
                ("pending_password", models.CharField(blank=True, max_length=255, verbose_name="Parol hash (kutilmoqda)")),
            ],
            options={
                "verbose_name": "Telegram OTP",
                "verbose_name_plural": "Telegram OTP kodlari",
                "ordering": ["-created_at"],
            },
        ),
    ]
