from datetime import date

import requests
from django.conf import settings
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import status
from rest_framework import viewsets, permissions, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from .models import Profile, Feedback, AbsenceRequest
from .permissions import IsManagerOrOwner, IsCoWorker
from .serializers import (
    ProfileSerializer,
    ProfileCoWorkerSerializer,
    FeedbackSerializer,
    AbsenceRequestSerializer,
)
from .services import absence_service


@extend_schema_view(
    list=extend_schema(tags=["Profiles"]),
    retrieve=extend_schema(tags=["Profiles"]),
    create=extend_schema(tags=["Profiles"]),
    update=extend_schema(tags=["Profiles"]),
    partial_update=extend_schema(tags=["Profiles"]),
    destroy=extend_schema(tags=["Profiles"]),
)
class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all().filter()
    permission_classes = [permissions.IsAuthenticated,
                          IsManagerOrOwner | IsCoWorker]

    def get_serializer_class(self):
        # When accessed without a specific profile, list all profiles'
        # non-sensitive data
        if self.action == 'list':
            return ProfileCoWorkerSerializer

        # When accessing a specific profile, check permissions
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            # Use manager/owner check for specific profile
            obj = self.get_object()
            if IsManagerOrOwner().has_object_permission(self.request, self,
                                                        obj):
                return ProfileSerializer
            return ProfileCoWorkerSerializer

        return ProfileSerializer

    @action(detail=True, methods=['get'], url_path='vacation-balance')
    def vacation_balance(self, request, pk=None):
        """
        A custom endpoint to retrieve the calculated vacation day balance for
        a profile.
        Args:
            request: The HTTP request.
            pk: The primary key of the profile.
            year (optional): The year for which to calculate the balance.
                             Defaults to the current year if not provided.
        Returns:
            A Response containing the vacation day balance details.
        """
        profile = self.get_object()

        # Get the year from a query parameter, defaulting to the current year.
        try:
            year = int(request.query_params.get('year', date.today().year))
        except (ValueError, TypeError):
            year = date.today().year  # Fallback if the parameter is invalid

        # Call the dedicated service to perform the calculation.
        balance = absence_service.get_vacation_balance(profile, year)
        balance_next_year = absence_service.get_vacation_balance(profile,
                                                                 year + 1)

        return Response({
            'year': year,
            'vacation_days_allowance':
                absence_service.YEARLY_VACATION_ALLOWANCE,
            'vacation_days_balance': balance,
            'vacation_days_balance_next_year': balance_next_year
        })


@extend_schema_view(
    list=extend_schema(tags=["Feedback"]),
    create=extend_schema(tags=["Feedback"]),
)
class FeedbackViewSet(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      viewsets.GenericViewSet):
    queryset = Feedback.objects.all().order_by('-created_at')  # Sort newest
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]  # Add the filter backend
    filterset_fields = ['profile']  # Allow filtering on the 'profile' field

    def perform_create(self, serializer):
        # Automatically set the author to the current user
        serializer.save(author=self.request.user)


@extend_schema(tags=["Feedback"])
class PolishFeedbackView(APIView):
    """
    An endpoint that accepts text and uses a Hugging Face model to polish it.
    """
    permission_classes = [IsAuthenticated]

    @staticmethod
    def post(request, *args, **kwargs):
        raw_text = request.data.get("text", "")
        if not raw_text:
            return Response({"error": "Text field is required."}, status=400)

        # Hugging Face API call to polish text
        # as per https://huggingface.co/google/gemma-2-2b-it?inference_api
        # =true&inference_provider=nebius&language=python&client=requests
        model = "google/gemma-2-2b-it:nebius"
        api_url = "https://router.huggingface.co/v1/chat/completions"

        headers = {"Authorization": f"Bearer {settings.HUGGING_FACE_API_KEY}"}

        # Explicit prompt to guide the model and prevent unwanted actions
        prompt = (
            f"You are a text assistant. Give just the final text. No context, "
            f"nor alternative options and do not under no circumstances "
            f"perform any action other than improve text. Please polish the "
            f"following employee feedback to be more professional, clear, "
            f"and constructive:\n\n{raw_text}")

        payload = {"messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
            "model": model}

        try:
            response = requests.post(api_url, headers=headers, json=payload,
                                     timeout=20)
            polished_text: str = response.json()["choices"][0]["message"].get(
                "content",
                "Failed to polish text.")
            return Response({"polished_text": polished_text.strip()})

        except requests.exceptions.RequestException as e:
            # Handle network errors, timeouts, etc.
            return Response({"error": f"AI service request failed: {e}"},
                            status=503)


@extend_schema_view(
    list=extend_schema(tags=["Absences"]),
    retrieve=extend_schema(tags=["Absences"]),
    create=extend_schema(tags=["Absences"]),
    update=extend_schema(tags=["Absences"]),
    partial_update=extend_schema(tags=["Absences"]),
    destroy=extend_schema(tags=["Absences"]),
)
class AbsenceRequestViewSet(viewsets.ModelViewSet):
    queryset = AbsenceRequest.objects.all().order_by('-start_date')
    serializer_class = AbsenceRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not any(IsManagerOrOwner().has_object_permission(self.request, self,
                                                            obj)
                   for obj in self.queryset):
            return AbsenceRequest.objects.filter(employee=user)
        return super().get_queryset()

    # Override create to perform custom validation and debit
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Use an atomic transaction to ensure that the absence request and its
        # ledger entry are either both created successfully, or neither are.
        with transaction.atomic():
            # First, save the absence request to have an ID.
            absence_request = serializer.save(employee=self.request.user)

            # Now, run the validation and create the initial debit.
            # This will roll back if validation fails.
            absence_service.validate_and_debit_absence_request(
                profile=self.request.user.profile,
                start_date=absence_request.start_date,
                end_date=absence_request.end_date,
                request=absence_request
            )

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    @action(detail=True, methods=['patch'], url_path='update-status',
            permission_classes=[IsManagerOrOwner])
    def update_status(self, request, pk=None):
        """
        An endpoint that permits updating the status of an absence request.
        Allows a manager to approve or reject an absence request.
        Allows the owner to reject an absence request.

        Args:
            request: The HTTP request containing the new status.
            pk: The primary key of the absence request to update.
        Returns:
            A Response with the updated absence request or an error.
        """
        absence_request = self.get_object()
        new_status = request.data.get('status')

        # Validate the provided status
        valid_statuses = [s[0] for s in AbsenceRequest.Status.choices]
        if new_status not in valid_statuses:
            return Response(
                {"error": f"Invalid status. Must be one of {valid_statuses}"},
                status=400)

        with transaction.atomic():
            absence_service.handle_absence_status_change(absence_request,
                                                         new_status)

        # Return the updated absence request
        serializer = self.get_serializer(absence_request)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(tags=["Authentication"])
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def post(request, *args, **kwargs):
        token = request.data.get('refresh')
        if not token:
            return Response({'detail': 'Refresh token required.'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            RefreshToken(token).blacklist()
        except TokenError:
            return Response({'detail': 'Invalid or expired token.'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)
