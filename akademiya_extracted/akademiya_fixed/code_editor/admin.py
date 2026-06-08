from django.contrib import admin
from django.utils.html import format_html
from .models import CodeChallenge, CodeSubmission


@admin.register(CodeChallenge)
class CodeChallengeAdmin(admin.ModelAdmin):
    list_display = ("title", "language", "difficulty", "submission_count", "is_active", "created_at")
    list_filter = ("language", "difficulty", "is_active")
    search_fields = ("title", "description")
    list_editable = ("is_active",)

    def submission_count(self, obj):
        return obj.submissions.count()
    submission_count.short_description = "Topshirmalar"


@admin.register(CodeSubmission)
class CodeSubmissionAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "language", "status", "is_public", "created_at", "code_preview")
    list_filter = ("language", "status", "is_public", "created_at")
    search_fields = ("user__email", "title", "code")
    readonly_fields = ("created_at", "updated_at", "code_display")

    fieldsets = (
        ("Asosiy ma'lumotlar", {"fields": ("user", "title", "language", "challenge", "status", "is_public")}),
        ("Kod", {"fields": ("code_display", "code")}),
        ("Vaqtlar", {"fields": ("created_at", "updated_at")}),
    )

    def code_preview(self, obj):
        snippet = obj.code[:100].replace("<", "&lt;").replace(">", "&gt;")
        return format_html('<code style="font-size:0.85em;background:#f5f5f5;padding:2px 6px;border-radius:3px">{}</code>', snippet)
    code_preview.short_description = "Kod (ko'rinish)"

    def code_display(self, obj):
        escaped = obj.code.replace("<", "&lt;").replace(">", "&gt;")
        return format_html(
            '<pre style="background:#1e1e1e;color:#d4d4d4;padding:16px;border-radius:8px;overflow:auto;max-height:400px">{}</pre>',
            escaped,
        )
    code_display.short_description = "Kod"
