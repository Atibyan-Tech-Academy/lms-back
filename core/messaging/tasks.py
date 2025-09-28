# LMS-BACK/messaging/tasks.py
from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth.models import User
from .models import Message

@shared_task
def process_ai_message(room_group_name, message, username):
    channel_layer = get_channel_layer()
    ai_response = f"AI says: Hello {username}! You said {message.replace('@ai', '').strip()}"
    # Save AI response
    sender = User.objects.get(username=username)
    Message.objects.create(
        sender=sender,
        receiver=sender,  # AI response to the sender
        body=ai_response,
        subject=f"AI Response in {room_group_name.replace('chat_', '')}"
    )
    async_to_sync(channel_layer.group_send)(
        room_group_name,
        {
            'type': 'chat_message',
            'message': ai_response,
            'username': 'AI',
        }
    )