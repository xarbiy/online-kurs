from django import forms
from .models import SupportTicket, TicketReply


class SupportTicketForm(forms.ModelForm):
    subject = forms.CharField(
        label="Mavzu",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Muammo yoki savolingizni qisqacha yozing",
        }),
    )
    category = forms.ChoiceField(
        label="Kategoriya",
        choices=SupportTicket.CATEGORY_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    priority = forms.ChoiceField(
        label="Ustuvorlik",
        choices=SupportTicket.PRIORITY_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    message = forms.CharField(
        label="Xabar",
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 5,
            "placeholder": "Muammo yoki savolingizni batafsil yozing...",
        }),
    )

    class Meta:
        model = SupportTicket
        fields = ("subject", "category", "priority", "message")


class TicketReplyForm(forms.ModelForm):
    message = forms.CharField(
        label="",
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 3,
            "placeholder": "Javobingizni yozing...",
        }),
    )

    class Meta:
        model = TicketReply
        fields = ("message",)
