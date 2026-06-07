from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from .models import Subject, Course, Lesson, Enrollment, LessonProgress


class SubjectModelTest(TestCase):
    def setUp(self):
        self.subject = Subject.objects.create(name="Matematika", slug="matematika")

    def test_subject_str(self):
        self.assertEqual(str(self.subject), "Matematika")


class CourseModelTest(TestCase):
    def setUp(self):
        self.subject = Subject.objects.create(name="Tarix", slug="tarix")
        self.course = Course.objects.create(
            subject=self.subject,
            title="O'zbekiston tarixi",
            slug="ozbekiston-tarixi",
            description="Tarix kursi",
            level="beginner",
        )

    def test_course_str(self):
        self.assertIn("Tarix", str(self.course))

    def test_lesson_count_empty(self):
        self.assertEqual(self.course.lesson_count(), 0)

    def test_lesson_count_with_lessons(self):
        Lesson.objects.create(course=self.course, title="1-dars", content="...", order=1)
        self.assertEqual(self.course.lesson_count(), 1)

    def test_enrolled_count(self):
        self.assertEqual(self.course.enrolled_count(), 0)


class CourseListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.subject = Subject.objects.create(name="Matematika", slug="matematika")
        self.course = Course.objects.create(
            subject=self.subject, title="Algebra", slug="algebra",
            description="Algebra kursi", level="beginner",
        )

    def test_course_list_page(self):
        response = self.client.get(reverse("course_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Algebra")

    def test_course_list_subject_filter(self):
        response = self.client.get(reverse("course_list") + "?subject=matematika")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Algebra")


class EnrollmentTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email="e@t.com", password="pass123", name="Test")
        self.subject = Subject.objects.create(name="Fizika", slug="fizika")
        self.course = Course.objects.create(
            subject=self.subject, title="Mexanika", slug="mexanika",
            description="Fizika kursi", level="beginner",
        )

    def test_enroll_requires_login(self):
        url = reverse("enroll_course", kwargs={"subject_slug": "fizika", "course_slug": "mexanika"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_enroll_authenticated(self):
        self.client.force_login(self.user)
        url = reverse("enroll_course", kwargs={"subject_slug": "fizika", "course_slug": "mexanika"})
        response = self.client.post(url)
        self.assertTrue(Enrollment.objects.filter(user=self.user, course=self.course).exists())
