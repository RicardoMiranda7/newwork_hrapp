from rest_framework import serializers

from .models import User, Profile, Feedback, AbsenceRequest


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email']


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'


class ProfileCoWorkerSerializer(serializers.ModelSerializer):
    """
    Serializer for co-workers, hiding sensitive data like salary.
    """

    class Meta:
        model = Profile
        exclude = ['salary', 'gender', 'date_of_birth', 'address',
                   'phone_number']  # Exclude sensitive fields


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'


class AbsenceRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AbsenceRequest
        fields = '__all__'
