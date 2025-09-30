# notes/urls.py
from rest_framework.routers import DefaultRouter
from .views import NoteViewSet

router = DefaultRouter()
router.register(r"notes", NoteViewSet, basename="notes")

<<<<<<< Updated upstream
urlpatterns = router.urls
=======
urlpatterns = router.urls
>>>>>>> Stashed changes
