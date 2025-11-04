from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)

    # Use email as the unique identifier for authentication
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    full_name = models.CharField(max_length=255)
    job_title = models.CharField(max_length=100)
    # Sensitive data field
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    # Non-sensitive data
    bio = models.TextField(blank=True)
    joined_at = models.DateTimeField(default=datetime(1970, 1, 1, 0, 0))
    department = models.CharField(max_length=100, blank=True)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="team_members")

    def __str__(self):
        return self.full_name

class Feedback(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="feedback")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="given_feedback")
    text = models.TextField()
    polished_text = models.TextField(blank=True) # For AI-polished version
    created_at = models.DateTimeField(auto_now_add=True)

class AbsenceRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="absence_requests")
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
