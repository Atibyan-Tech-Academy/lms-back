"""
URL configuration for lms_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
<<<<<<< Updated upstream:lms_backend/lms_backend/urls.py
]
=======
    path('api/accounts/', include('accounts.urls')),  # Auth and user management
    path('api/courses/', include('courses.urls')),    # Course-related endpoints
    path('api/assignments/', include('assignments.urls')),  # Assignment endpoints
    path('api/messaging/', include('messaging.urls')),     # Messaging endpoints
    path('api/certificates/', include('certificates.urls')),  # Certificate endpoints
    path("api/editprofile/", include("editprofile.urls")),  # editprofile endpoints
    path('api/', include('notes.urls')),
<<<<<<< Updated upstream:lms_backend/lms_backend/urls.py
<<<<<<< Updated upstream:lms_backend/lms_backend/urls.py
]
>>>>>>> Stashed changes:core/core/urls.py
=======
]
>>>>>>> Stashed changes:core/core/urls.py
=======

]
>>>>>>> Stashed changes:core/core/urls.py
