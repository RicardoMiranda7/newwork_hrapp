from rest_framework import viewsets, permissions

from .models import Profile, Feedback, AbsenceRequest
from .permissions import IsManagerOrOwner, IsCoWorker
from .serializers import (
    ProfileSerializer,
    ProfileCoWorkerSerializer,
    FeedbackSerializer,
    AbsenceRequestSerializer,
)


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all().filter()
    permission_classes = [permissions.IsAuthenticated, IsManagerOrOwner | IsCoWorker]

    def get_serializer_class(self):
        if self.action == 'list':
            return ProfileCoWorkerSerializer

        if self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            # Use manager/owner check for specific profile
            obj = self.get_object()
            if IsManagerOrOwner().has_object_permission(self.request, self, obj):
                return ProfileSerializer
            return ProfileCoWorkerSerializer

        return ProfileSerializer


class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Automatically set the author to the current user
        serializer.save(author=self.request.user)


class AbsenceRequestViewSet(viewsets.ModelViewSet):
    queryset = AbsenceRequest.objects.all()
    serializer_class = AbsenceRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Check if user is manager/owner instead of role
        user = self.request.user
        if not any(IsManagerOrOwner().has_object_permission(self.request, self,
                                                            obj)
                   for obj in self.queryset):
            return AbsenceRequest.objects.filter(employee=user)
        return super().get_queryset()

    def perform_create(self, serializer):
        serializer.save(employee=self.request.user)
