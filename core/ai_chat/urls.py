from django.urls import path
from .views import AIChatView

urlpatterns = [
    path("ask/", AIChatView.as_view(), name="ai-chat"),
]
