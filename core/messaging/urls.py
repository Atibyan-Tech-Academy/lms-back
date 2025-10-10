from django.urls import path
from .views import ChatRoomListCreateView, MessageListView, UserListView

urlpatterns = [
    path("chatrooms/", ChatRoomListCreateView.as_view(), name="chatroom-list-create"),
    path("chatrooms/<int:room_id>/messages/", MessageListView.as_view(), name="message-list"),
    path("users/", UserListView.as_view(), name="user-list"),
]