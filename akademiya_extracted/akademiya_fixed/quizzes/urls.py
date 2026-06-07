from django.urls import path
from . import views

urlpatterns = [
    path("", views.quiz_list, name="quiz_list"),
    path("<int:quiz_id>/", views.quiz_detail, name="quiz_detail"),
    path("<int:quiz_id>/start/", views.start_quiz, name="start_quiz"),
    path("attempt/<int:attempt_id>/", views.take_quiz, name="take_quiz"),
    path("result/<int:result_id>/", views.quiz_result, name="quiz_result"),
    path("my-results/", views.my_results, name="my_results"),
]
