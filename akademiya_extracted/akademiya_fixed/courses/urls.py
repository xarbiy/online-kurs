from django.urls import path
from . import views

urlpatterns = [
    path("", views.course_list, name="course_list"),
    path("<slug:subject_slug>/<slug:course_slug>/", views.course_detail, name="course_detail"),
    path("<slug:subject_slug>/<slug:course_slug>/enroll/", views.enroll_course, name="enroll_course"),
    path("<slug:subject_slug>/<slug:course_slug>/lesson/<int:lesson_id>/", views.lesson_view, name="lesson_view"),
]
