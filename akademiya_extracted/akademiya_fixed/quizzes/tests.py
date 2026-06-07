from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from courses.models import Subject
from .models import Quiz, Question, Answer, QuizAttempt, QuizResult


class QuizModelTest(TestCase):
    def setUp(self):
        self.subject = Subject.objects.create(name="Matematika", slug="matematika")
        self.quiz = Quiz.objects.create(
            subject=self.subject,
            title="Algebra testi",
            time_limit=30,
            pass_score=70,
        )
        self.question = Question.objects.create(quiz=self.quiz, text="2 + 2 = ?", order=1)
        self.correct_answer = Answer.objects.create(question=self.question, text="4", is_correct=True)
        self.wrong_answer = Answer.objects.create(question=self.question, text="5", is_correct=False)

    def test_quiz_str(self):
        self.assertEqual(str(self.quiz), "Algebra testi")

    def test_question_count(self):
        self.assertEqual(self.quiz.question_count(), 1)

    def test_answer_str(self):
        self.assertIn("✓", str(self.correct_answer))
        self.assertIn("✗", str(self.wrong_answer))


class QuizFlowTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email="quiz@t.com", password="pass123", name="Quiz User")
        self.subject = Subject.objects.create(name="Fizika", slug="fizika")
        self.quiz = Quiz.objects.create(subject=self.subject, title="Mexanika testi", pass_score=50)
        self.q1 = Question.objects.create(quiz=self.quiz, text="Savol 1", order=1)
        self.a1_correct = Answer.objects.create(question=self.q1, text="To'g'ri", is_correct=True)
        self.a1_wrong = Answer.objects.create(question=self.q1, text="Noto'g'ri", is_correct=False)

    def test_quiz_list_requires_login(self):
        response = self.client.get(reverse("quiz_list"))
        self.assertEqual(response.status_code, 302)

    def test_quiz_list_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("quiz_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mexanika testi")

    def test_start_quiz(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("start_quiz", kwargs={"quiz_id": self.quiz.id}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(QuizAttempt.objects.filter(user=self.user, quiz=self.quiz).exists())

    def test_quiz_submission_correct_answer(self):
        self.client.force_login(self.user)
        attempt = QuizAttempt.objects.create(user=self.user, quiz=self.quiz, status="in_progress")
        response = self.client.post(
            reverse("take_quiz", kwargs={"attempt_id": attempt.id}),
            {f"question_{self.q1.id}": self.a1_correct.id},
        )
        self.assertEqual(response.status_code, 302)
        result = QuizResult.objects.get(user=self.user, quiz=self.quiz)
        self.assertEqual(result.correct_answers, 1)
        self.assertEqual(result.score, 100.0)
        self.assertTrue(result.passed)

    def test_quiz_submission_wrong_answer(self):
        self.client.force_login(self.user)
        attempt = QuizAttempt.objects.create(user=self.user, quiz=self.quiz, status="in_progress")
        self.client.post(
            reverse("take_quiz", kwargs={"attempt_id": attempt.id}),
            {f"question_{self.q1.id}": self.a1_wrong.id},
        )
        result = QuizResult.objects.get(user=self.user, quiz=self.quiz)
        self.assertEqual(result.correct_answers, 0)
        self.assertEqual(result.score, 0.0)
        self.assertFalse(result.passed)

    def test_my_results(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("my_results"))
        self.assertEqual(response.status_code, 200)
