from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from .models import User


class RegisterForm(UserCreationForm):
    name = forms.CharField(
        max_length=150,
        label="To'liq ism",
        widget=forms.TextInput(attrs={
            "placeholder": "Ismingiz va familiyangiz",
            "class": "form-control form-control-lg",
            "autofocus": True,
        }),
    )
    email = forms.EmailField(
        label="Email manzil",
        widget=forms.EmailInput(attrs={
            "placeholder": "email@example.com",
            "class": "form-control form-control-lg",
        }),
    )
    password1 = forms.CharField(
        label="Parol",
        widget=forms.PasswordInput(attrs={
            "placeholder": "Kamida 8 ta belgi",
            "class": "form-control form-control-lg",
            "id": "id_password1",
        }),
    )
    password2 = forms.CharField(
        label="Parolni tasdiqlang",
        widget=forms.PasswordInput(attrs={
            "placeholder": "Parolni qayta kiriting",
            "class": "form-control form-control-lg",
            "id": "id_password2",
        }),
    )

    class Meta:
        model = User
        fields = ("name", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get("email", "").lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Bu email allaqachon ro'yxatdan o'tgan.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.auth_method = User.AUTH_METHOD_EMAIL
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(
        label="Email manzil",
        widget=forms.EmailInput(attrs={
            "placeholder": "email@example.com",
            "class": "form-control form-control-lg",
            "autofocus": True,
        }),
    )
    password = forms.CharField(
        label="Parol",
        widget=forms.PasswordInput(attrs={
            "placeholder": "Parolingiz",
            "class": "form-control form-control-lg",
            "id": "id_password",
        }),
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email", "").lower()
        password = cleaned_data.get("password")
        if email and password:
            user = authenticate(username=email, password=password)
            if user is None:
                raise forms.ValidationError("Email yoki parol noto'g'ri.")
            if not user.is_active:
                raise forms.ValidationError("Hisob faolsizlantirilgan.")
            cleaned_data["user"] = user
        return cleaned_data


class TelegramRegisterForm(forms.Form):
    """Telegram orqali ro'yxatdan o'tish — 1-qadam: ism, email, parol."""
    name = forms.CharField(
        max_length=150,
        label="To'liq ism",
        widget=forms.TextInput(attrs={
            "placeholder": "Ismingiz va familiyangiz",
            "class": "form-control form-control-lg",
            "autofocus": True,
        }),
    )
    email = forms.EmailField(
        label="Email manzil",
        widget=forms.EmailInput(attrs={
            "placeholder": "email@example.com",
            "class": "form-control form-control-lg",
        }),
    )
    password1 = forms.CharField(
        label="Parol",
        widget=forms.PasswordInput(attrs={
            "placeholder": "Kamida 8 ta belgi",
            "class": "form-control form-control-lg",
            "id": "id_tg_password1",
        }),
    )
    password2 = forms.CharField(
        label="Parolni tasdiqlang",
        widget=forms.PasswordInput(attrs={
            "placeholder": "Parolni qayta kiriting",
            "class": "form-control form-control-lg",
            "id": "id_tg_password2",
        }),
    )

    def clean_email(self):
        email = self.cleaned_data.get("email", "").lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Bu email allaqachon ro'yxatdan o'tgan.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Parollar mos kelmadi.")
        if p1 and len(p1) < 8:
            raise forms.ValidationError("Parol kamida 8 ta belgidan iborat bo'lishi kerak.")
        return cleaned_data


class TelegramLoginForm(forms.Form):
    """Telegram orqali kirish — foydalanuvchi mavjud, OTP yuboriladi."""
    phone_number = forms.CharField(
        max_length=20,
        label="Telefon raqam",
        widget=forms.TextInput(attrs={
            "placeholder": "+998901234567",
            "class": "form-control form-control-lg",
            "autofocus": True,
        }),
        help_text="Telegram botga bog'langan telefon raqamingiz",
    )

    def clean_phone_number(self):
        phone = self.cleaned_data.get("phone_number", "").strip()
        # Raqamni normallashtirish
        if phone.startswith("8") and len(phone) == 9:
            phone = "+998" + phone
        elif phone.startswith("998") and len(phone) == 12:
            phone = "+" + phone
        if not phone.startswith("+"):
            phone = "+" + phone
        return phone


class OTPVerifyForm(forms.Form):
    """OTP kodni tasdiqlash formasi."""
    code = forms.CharField(
        max_length=6,
        min_length=6,
        label="Tasdiqlash kodi",
        widget=forms.TextInput(attrs={
            "placeholder": "● ● ● ● ● ●",
            "class": "form-control form-control-lg text-center otp-input",
            "maxlength": "6",
            "inputmode": "numeric",
            "pattern": "[0-9]{6}",
            "autofocus": True,
            "autocomplete": "one-time-code",
        }),
    )

    def clean_code(self):
        code = self.cleaned_data.get("code", "").strip()
        if not code.isdigit():
            raise forms.ValidationError("Kod faqat raqamlardan iborat bo'lishi kerak.")
        return code


class ProfileForm(forms.ModelForm):
    name = forms.CharField(
        label="To'liq ism",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    bio = forms.CharField(
        label="Bio",
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "O'zingiz haqingizda..."}),
    )
    avatar = forms.ImageField(
        label="Avatar",
        required=False,
        widget=forms.FileInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = User
        fields = ("name", "bio", "avatar")
