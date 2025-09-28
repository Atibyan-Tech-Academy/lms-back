# LMS-BACK/messaging/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import User
from channels.db import database_sync_to_async
from .models import Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        # Get JWT from query string
        token = self.scope['query_string'].decode().split('token=')[-1]
        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            self.user = await database_sync_to_async(User.objects.get)(id=user_id)
        except Exception:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        receiver_username = data.get('receiver')  # Optional: Add receiver if needed

        # Save message to database
        await self.save_message(message, receiver_username)

        if message.startswith('@ai'):
            from .tasks import process_ai_message
            process_ai_message.delay(self.room_group_name, message, self.user.username)
        else:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': self.user.username,
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
        }))

    @database_sync_to_async
    def save_message(self, message, receiver_username=None):
        receiver = None
        if receiver_username:
            try:
                receiver = User.objects.get(username=receiver_username)
            except User.DoesNotExist:
                pass  # Fallback to broadcast if receiver not found
        Message.objects.create(
            sender=self.user,
            receiver=receiver if receiver else self.user,  # Default to self if no receiver
            body=message,
            subject=f"Chat in {self.room_id}"
        )