from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProfileViewSet, FeedbackViewSet, AbsenceRequestViewSet

router = DefaultRouter()
router.register(r'profiles', ProfileViewSet)
router.register(r'feedback', FeedbackViewSet)
router.register(r'absences', AbsenceRequestViewSet)

urlpatterns = [
    path('', include(router.urls)),
]