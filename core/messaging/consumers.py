import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from .models import ChatRoom, Message

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_id}"

        try:
            token = None
            if 'token' in self.scope['query_string'].decode().split('='):
                token = self.scope['query_string'].decode().split('=')[1]
            elif await self.receive_token():
                token = self.received_token

            if token:
                user = await self.get_user_from_token(token)
                self.scope['user'] = user
            else:
                await self.close()
                return
        except (InvalidToken, TokenError):
            await self.close()
            return

        if await self.is_user_in_room():
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
            await self.mark_messages_read()
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        if 'token' in text_data_json:
            self.received_token = text_data_json['token']
            return
        if 'typing' in text_data_json:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "typing_indicator",
                    "sender": self.scope["user"].username,
                    "typing": text_data_json["typing"],
                },
            )
            return
        if 'read' in text_data_json:
            await self.mark_messages_read()
            return

        message = text_data_json["message"]
        user = self.scope["user"]
        message_obj = await self.save_message(user, message)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "sender": user.username,
                "timestamp": str(message_obj.timestamp),
                "message_id": message_obj.id,
            },
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "message",
            "message": event["message"],
            "sender": event["sender"],
            "timestamp": event["timestamp"],
            "message_id": event["message_id"],
        }))

    async def typing_indicator(self, event):
        await self.send(text_data=json.dumps({
            "type": "typing",
            "sender": event["sender"],
            "typing": event["typing"],
        }))

    @database_sync_to_async
    def is_user_in_room(self):
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            return room.participants.filter(id=self.scope["user"].id).exists()
        except ChatRoom.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, user, content):
        room = ChatRoom.objects.get(id=self.room_id)
        return Message.objects.create(room=room, sender=user, content=content)

    @database_sync_to_async
    def get_user_from_token(self, token):
        validated_token = AccessToken(token)
        user_id = validated_token['user_id']
        return User.objects.get(id=user_id)

    @database_sync_to_async
    def mark_messages_read(self):
        room = ChatRoom.objects.get(id=self.room_id)
        user = self.scope["user"]
        messages = room.messages.exclude(read_by=user)
        for message in messages:
            message.read_by.add(user)
        return True

    async def receive_token(self):
        return await self.receive(text_data=None)