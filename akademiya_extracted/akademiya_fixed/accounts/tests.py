from django.test import TestCase, Client
from django.urls import reverse
from .models import User


class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            name="Test Foydalanuvchi",
        )

    def test_user_creation(self):
        self.assertEqual(self.user.email, "test@example.com")
        self.assertEqual(self.user.name, "Test Foydalanuvchi")
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)

    def test_user_str(self):
        self.assertEqual(str(self.user), "test@example.com")

    def test_get_full_name(self):
        self.assertEqual(self.user.get_full_name(), "Test Foydalanuvchi")

    def test_get_short_name(self):
        self.assertEqual(self.user.get_short_name(), "Test")

    def test_superuser_creation(self):
        admin = User.objects.create_superuser(
            email="admin@example.com",
            password="adminpass123",
            name="Admin",
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_email_unique(self):
        with self.assertRaises(Exception):
            User.objects.create_user(
                email="test@example.com",
                password="anotherpass",
                name="Another",
            )


class RegisterViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("register")

    def test_get_register_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ro'yxatdan o'tish")

    def test_valid_registration(self):
        response = self.client.post(self.url, {
            "name": "Yangi Foydalanuvchi",
            "email": "new@example.com",
            "password1": "kompleksparol123!",
            "password2": "kompleksparol123!",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email="new@example.com").exists())

    def test_duplicate_email(self):
        User.objects.create_user(email="existing@example.com", password="pass123", name="Mavjud")
        response = self.client.post(self.url, {
            "name": "Yangi",
            "email": "existing@example.com",
            "password1": "pass123456!",
            "password2": "pass123456!",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "allaqachon")

    def test_password_mismatch(self):
        response = self.client.post(self.url, {
            "name": "Test",
            "email": "test2@example.com",
            "password1": "pass123456!",
            "password2": "different123!",
        })
        self.assertEqual(response.status_code, 200)


class LoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("login")
        self.user = User.objects.create_user(
            email="login@example.com",
            password="testpass123",
            name="Login Test",
        )

    def test_get_login_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Kirish")

    def test_valid_login(self):
        response = self.client.post(self.url, {
            "email": "login@example.com",
            "password": "testpass123",
        })
        self.assertEqual(response.status_code, 302)

    def test_invalid_password(self):
        response = self.client.post(self.url, {
            "email": "login@example.com",
            "password": "wrongpassword",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "noto'g'ri")

    def test_nonexistent_email(self):
        response = self.client.post(self.url, {
            "email": "nobody@example.com",
            "password": "somepassword",
        })
        self.assertEqual(response.status_code, 200)


class DashboardViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="dash@example.com",
            password="testpass123",
            name="Dashboard User",
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("dashboard"))
        self.assertRedirects(response, "/accounts/login/?next=/accounts/dashboard/")

    def test_dashboard_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dashboard")
