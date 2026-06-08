from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = "Akademiya Boshqaruv Paneli"
admin.site.site_title = "Akademiya Admin"
admin.site.index_title = "Boshqaruv bo'limi"

urlpatterns = [
    path("admin/",    admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("auth/",     include("allauth.urls")),   # Google OAuth uchun
    path("courses/",  include("courses.urls")),
    path("quizzes/",  include("quizzes.urls")),
    path("code/",     include("code_editor.urls")),
    path("support/",  include("support.urls")),
    path("",          include("accounts.urls_home")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
