from django.urls import path
from . import views

urlpatterns = [
    path("submit/", views.submit_support_ticket, name="submit_support_ticket"),
]
