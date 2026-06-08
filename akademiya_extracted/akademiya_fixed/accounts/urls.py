from django.urls import path
from . import views

urlpatterns = [
    # Email auth
    path("register/",  views.register_view,  name="register"),
    path("login/",     views.login_view,      name="login"),
    path("logout/",    views.logout_view,     name="logout"),

    # Profil va dashboard
    path("profile/",   views.profile_view,   name="profile"),
    path("dashboard/", views.dashboard_view, name="dashboard"),

    # Telegram ro'yxatdan o'tish
    path("telegram/register/",        views.telegram_register_start,  name="telegram_register_start"),
    path("telegram/register/bot/",    views.telegram_register_bot,    name="telegram_register_bot"),
    path("telegram/register/verify/", views.telegram_register_verify, name="telegram_register_verify"),

    # Telegram login
    path("telegram/login/",           views.telegram_login_view,   name="telegram_login"),
    path("telegram/login/verify/",    views.telegram_login_verify, name="telegram_login_verify"),

    # Telegram bot webhook
    path("telegram/webhook/",         views.telegram_webhook, name="telegram_webhook"),
]
