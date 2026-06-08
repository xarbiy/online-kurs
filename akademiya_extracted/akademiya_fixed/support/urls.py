from django.urls import path
from . import views

urlpatterns = [
    path("",              views.ticket_list,   name="support"),
    path("new/",          views.create_ticket, name="create_ticket"),
    path("<int:pk>/",     views.ticket_detail, name="ticket_detail"),
    path("<int:pk>/close/", views.close_ticket, name="close_ticket"),
]
