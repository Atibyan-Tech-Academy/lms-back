from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import AIChatMessage
from .serializers import AIChatMessageSerializer
from decouple import config
import requests
from django.contrib.auth import get_user_model

User = get_user_model()

class AIChatView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        messages = AIChatMessage.objects.filter(user=request.user).order_by('timestamp')
        serializer = AIChatMessageSerializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request):
        user_message = request.data.get('message')
        if not user_message:
            return Response({"error": "Message required"}, status=status.HTTP_400_BAD_REQUEST)

        # Save user message
        AIChatMessage.objects.create(user=request.user, message=user_message, is_ai_response=False)

        # Role-based prompt
        role = request.user.groups.first().name if request.user.groups.exists() else 'user'
        if role == 'STUDENT':
            prompt = f"You are an AI assistant helping a student with their coursework. Provide clear, educational responses. Question: {user_message}"
        elif role == 'LECTURER':
            prompt = f"You are an AI assistant helping an instructor create course content. Suggest ideas, structure, or resources. Request: {user_message}"
        elif role == 'ADMIN':
            prompt = f"You are an AI assistant helping an LMS admin with platform management tasks. Provide guidance on user management, settings, or analytics. Request: {user_message}"
        else:
            prompt = user_message

        # Call Hugging Face API
        hf_api_url = config("HF_API_URL")
        hf_api_token = config("HF_API_TOKEN")
        headers = {"Authorization": f"Bearer {hf_api_token}"}
        data = {"inputs": prompt}
        try:
            response = requests.post(hf_api_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            ai_response = response.json()[0]['generated_text']
            AIChatMessage.objects.create(user=request.user, message=ai_response, is_ai_response=True)
            return Response({"ai_response": ai_response})
        except requests.exceptions.Timeout:
            print("HF API timed out")
            return Response({"error": "AI response timed out. Try again later."}, status=status.HTTP_504_GATEWAY_TIMEOUT)
        except requests.exceptions.HTTPError as e:
            print(f"HF API Error: {e.response.status_code} - {e.response.text}")
            return Response({"error": f"AI service error: {e.response.status_code}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return Response({"error": "AI response failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)