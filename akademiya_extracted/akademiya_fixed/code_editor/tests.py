from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from .models import CodeSubmission, CodeChallenge


class CodeChallengeModelTest(TestCase):
    def setUp(self):
        self.challenge = CodeChallenge.objects.create(
            title="Fibonacci",
            description="Fibonacci sonini hisoblang",
            language="python",
            starter_code="def fibonacci(n):\n    pass",
            difficulty="easy",
        )

    def test_challenge_str(self):
        self.assertEqual(str(self.challenge), "Fibonacci")


class CodeSubmissionTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email="coder@t.com", password="pass123", name="Coder")

    def test_editor_home_requires_login(self):
        response = self.client.get(reverse("editor_home"))
        self.assertEqual(response.status_code, 302)

    def test_editor_home_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("editor_home"))
        self.assertEqual(response.status_code, 200)

    def test_create_submission(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("new_submission"), {
            "title": "Mening birinchi kodum",
            "language": "python",
            "code": "print('Salom dunyo!')",
            "status": "submitted",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(CodeSubmission.objects.filter(user=self.user, title="Mening birinchi kodum").exists())

    def test_view_own_submission(self):
        self.client.force_login(self.user)
        submission = CodeSubmission.objects.create(
            user=self.user, title="Test", language="python", code="x = 1"
        )
        response = self.client.get(reverse("view_submission", kwargs={"submission_id": submission.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test")

    def test_cannot_view_private_submission(self):
        other = User.objects.create_user(email="other@t.com", password="pass123", name="Other")
        submission = CodeSubmission.objects.create(
            user=other, title="Private", language="python", code="x = 2", is_public=False
        )
        self.client.force_login(self.user)
        response = self.client.get(reverse("view_submission", kwargs={"submission_id": submission.id}))
        self.assertEqual(response.status_code, 302)

    def test_delete_submission(self):
        self.client.force_login(self.user)
        submission = CodeSubmission.objects.create(
            user=self.user, title="Delete me", language="python", code="x = 3"
        )
        self.client.post(reverse("delete_submission", kwargs={"submission_id": submission.id}))
        self.assertFalse(CodeSubmission.objects.filter(id=submission.id).exists())
