from django.contrib import admin
from .models import SupportTicket, TicketReply


class TicketReplyInline(admin.TabularInline):
    model = TicketReply
    extra = 1
    fields = ("user", "message", "is_staff_reply", "created_at")
    readonly_fields = ("created_at",)


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ("ticket_number", "user", "subject", "category", "priority", "status", "created_at")
    list_filter = ("status", "priority", "category")
    search_fields = ("ticket_number", "user__email", "subject")
    readonly_fields = ("ticket_number", "created_at", "updated_at")
    inlines = [TicketReplyInline]
    ordering = ("-created_at",)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, TicketReply) and not instance.pk:
                instance.user = request.user
                instance.is_staff_reply = True
            instance.save()
        formset.save_m2m()
