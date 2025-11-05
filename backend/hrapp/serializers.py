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
                   'phone_number', 'user', 'manager', 'id']  # Exclude sensitive fields


class FeedbackSerializer(serializers.ModelSerializer):
    # Set author to be read-only as it is set automatically in the view.
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Feedback
        fields = '__all__'


class AbsenceRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AbsenceRequest
        fields = '__all__'
