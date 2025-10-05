from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
from .models import SupportTicket
from .serializers import SupportTicketSerializer


@api_view(["POST"])
@permission_classes([AllowAny])
def submit_support_ticket(request):
    serializer = SupportTicketSerializer(data=request.data)
    if serializer.is_valid():
        ticket = serializer.save()

        # --- Email to admin ---
        subject = f"New Support Request: {ticket.subject}"
        message = (
            f"Name: {ticket.name}\n"
            f"Email: {ticket.email}\n\n"
            f"Message:\n{ticket.message}"
        )

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,  # sender
            [settings.ADMIN_EMAIL],       # recipient (admin)
            fail_silently=False,
        )

        return Response(
            {"message": "✅ Support request submitted successfully!"},
            status=status.HTTP_201_CREATED,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
