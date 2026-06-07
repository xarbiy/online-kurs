from django.urls import path
from . import views

urlpatterns = [
    path("", views.editor_home, name="editor_home"),
    path("new/", views.new_submission, name="new_submission"),
    path("run/", views.run_code, name="run_code"),
    path("<int:submission_id>/", views.view_submission, name="view_submission"),
    path("<int:submission_id>/edit/", views.edit_submission, name="edit_submission"),
    path("<int:submission_id>/delete/", views.delete_submission, name="delete_submission"),
    path("challenge/<int:challenge_id>/", views.challenge_detail, name="challenge_detail"),
]
