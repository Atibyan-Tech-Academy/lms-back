import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from decouple import config
from .models import AIChatMessage
from .serializers import AIChatMessageSerializer

class AIChatView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return chat history for the logged-in user"""
        messages = AIChatMessage.objects.filter(user=request.user)
        serializer = AIChatMessageSerializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Send user message to AI, save both user and AI reply"""
        user_message = request.data.get("message", "")
        if not user_message.strip():
            return Response({"reply": "Please enter a message."})

        # Save user message
        AIChatMessage.objects.create(user=request.user, sender="user", text=user_message)

        # Call Hugging Face API
        api_key = config("HF_API_KEY")
        headers = {"Authorization": f"Bearer {api_key}"}
        payload = {"inputs": user_message}

        try:
            res = requests.post(
                "https://api-inference.huggingface.co/models/distilgpt2",
                headers=headers,
                json=payload,
                timeout=20,
            )
            if res.status_code == 200:
                data = res.json()
                reply = data[0]["generated_text"]
            else:
                reply = "⚠️ AI is busy, please try again later."
        except Exception as e:
            reply = f"⚠️ Error: {str(e)}"

        # Save AI reply
        AIChatMessage.objects.create(user=request.user, sender="ai", text=reply)

        return Response({"reply": reply})
