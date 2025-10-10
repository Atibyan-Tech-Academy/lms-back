from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer, UserSerializer
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class ChatRoomListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        rooms = ChatRoom.objects.filter(participants=user)
        if user.groups.filter(name='student').exists():
            rooms = rooms.filter(participants__groups__name__in=['instructor', 'admin'])
        serializer = ChatRoomSerializer(rooms, many=True)
        return Response(serializer.data)

    def post(self, request):
        user = request.user
        participant_id = request.data.get('participant_id')
        is_one_on_one = request.data.get('is_one_on_one', False)

        if is_one_on_one and participant_id:
            try:
                participant = User.objects.get(id=participant_id)
                # Role restrictions: Students can only chat with instructors/admins
                if user.groups.filter(name='student').exists() and not participant.groups.filter(name__in=['instructor', 'admin']).exists():
                    return Response({"error": "Students can only chat with instructors or admins"}, status=status.HTTP_403_FORBIDDEN)

                # Check for existing one-on-one chat
                existing_room = ChatRoom.objects.filter(
                    is_one_on_one=True,
                    participants=user
                ).filter(participants=participant).distinct()
                if existing_room.exists():
                    return Response(ChatRoomSerializer(existing_room.first()).data, status=status.HTTP_200_OK)

                # Create new one-on-one chat
                room = ChatRoom.objects.create(is_one_on_one=True)
                room.participants.add(user, participant)
                return Response(ChatRoomSerializer(room).data, status=status.HTTP_201_CREATED)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Group chat creation
            serializer = ChatRoomSerializer(data=request.data)
            if serializer.is_valid():
                room = serializer.save()
                room.participants.add(user)
                if user.groups.filter(name='admin').exists() and request.data.get('admin_only'):
                    room.participants.set(User.objects.filter(groups__name='admin'))
                return Response(ChatRoomSerializer(room).data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MessageListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, room_id):
        try:
            room = ChatRoom.objects.get(id=room_id, participants=request.user)
            messages = room.messages.all()
            serializer = MessageSerializer(messages, many=True)
            return Response(serializer.data)
        except ChatRoom.DoesNotExist:
            return Response({"error": "Room not found or access denied"}, status=status.HTTP_404_NOT_FOUND)

class UserListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.groups.filter(name='student').exists():
            users = User.objects.filter(groups__name__in=['instructor', 'admin'])
        else:
            users = User.objects.exclude(id=user.id)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)