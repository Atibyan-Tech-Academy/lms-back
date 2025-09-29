from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/courses/', include('courses.urls')),
    path('api/assignments/', include('assignments.urls')),
    path('api/messaging/', include('messaging.urls')),   # ✅ Messaging
    path('api/certificates/', include('certificates.urls')),
    path("api/editprofile/", include("editprofile.urls")),
    path("api/ai/", include("ai_chat.urls")),

]
