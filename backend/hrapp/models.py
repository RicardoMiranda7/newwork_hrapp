from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models


# Custom User model extending AbstractUser to use email as username
class User(AbstractUser):
    email = models.EmailField(unique=True)

    # Tell Django to use the 'email' field for authentication instead of
    # 'username'.
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]


# The central model representing an employee's profile.
# It has a one-to-one relationship with the User model.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                related_name="profile")
    full_name = models.CharField(max_length=255)
    job_title = models.CharField(max_length=100)

    # Sensitive data field
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True,
                                 blank=True)
    gender = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)

    # Non-sensitive data
    bio = models.TextField(blank=True)
    joined_at = models.DateTimeField(default=datetime(1970, 1, 1, 0, 0))
    department = models.CharField(max_length=100, blank=True)

    # Link the profile to a manager (another User), defines the reporting
    # structure.
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                blank=True, related_name="team_members")

    def __str__(self):
        return self.full_name


# Stores feedback given by one user (author) to another (profile).
class Feedback(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE,
                                related_name="feedback")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="given_feedback")
    text = models.TextField()
    polished_text = models.TextField(blank=True)  # For AI-polished version
    created_at = models.DateTimeField(auto_now_add=True)


# Represents an employee's request for time off.
class AbsenceRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    employee = models.ForeignKey(User, on_delete=models.CASCADE,
                                 related_name="absence_requests")
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices,
                              default=Status.PENDING)

# Stores official bank holidays to be excluded from vacation calculations
class BankHoliday(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField(unique=True)

    def __str__(self):
        return f"{self.name} ({self.date})"

    class Meta:
        ordering = ['date']


class AbsenceLedger(models.Model):
    """
    An immutable ledger for tracking vacation day transactions.
    - Positive amounts are credits (e.g., yearly allowance, rejected requests).
    - Negative amounts are debits (e.g., new or approved requests).
    """
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE,
                                related_name="ledger_entries")
    # A nullable ForeignKey allows for transactions not tied to a specific
    # request (e.g., initial allowance).
    absence_request = models.ForeignKey(AbsenceRequest,
                                        on_delete=models.SET_NULL,
                                        related_name="ledger_entries",
                                        null=True,
                                        blank=True)

    amount = models.IntegerField()  # The number of days for this transaction
    # (+ or -)
    year = models.IntegerField()  # The year this transaction applies to

    # A short description for clarity in the admin panel.
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (f"{self.profile.full_name} | {self.amount} days in {self.year} "
                f"({self.description})")

    class Meta:
        ordering = ['-created_at']
