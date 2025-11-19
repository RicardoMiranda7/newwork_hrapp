from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.exceptions import ValidationError

from hrapp.models import Profile, AbsenceRequest, BankHoliday
from hrapp.services import absence_service

# Get the custom User model
User = get_user_model()


class AbsenceServiceTestCase(TestCase):
    """
    Test suite for the absence_service layer.
    This class sets up a consistent environment with a manager and two
    employees.
    """

    def setUp(self):
        """
        Set up the necessary objects for each test.
        This method runs before every single test function.
        """
        # 1. Create Users
        self.manager = User.objects.create_user(
            username='manager', email='manager@example.com',
            password='password123'
        )
        self.employee1 = User.objects.create_user(
            username='employee1', email='employee1@example.com',
            password='password123'
        )
        self.employee2 = User.objects.create_user(
            username='employee2', email='employee2@example.com',
            password='password123'
        )

        # 2. Create Profiles and link them to users and the manager
        self.profile1 = Profile.objects.create(
            user=self.employee1, full_name="Employee One", manager=self.manager
        )
        self.profile2 = Profile.objects.create(
            user=self.employee2, full_name="Employee Two", manager=self.manager
        )

        # 3. Create Bank Holidays for testing
        BankHoliday.objects.create(name="New Year's Day", date=date(2025, 1, 1))
        BankHoliday.objects.create(name="Christmas Day",
                                   date=date(2025, 12, 25))
        BankHoliday.objects.create(name="New Year's Day 2026",
                                   date=date(2026, 1, 1))

    # --- Test Cases for get_vacation_balance ---

    def test_get_vacation_balance_initial_allowance(self):
        """
        Test that the initial yearly allowance is correctly granted on the
        first balance check.
        """
        balance = absence_service.get_vacation_balance(self.profile1, 2025)
        self.assertEqual(balance, absence_service.YEARLY_VACATION_ALLOWANCE)
        # Verify that a ledger entry was created
        self.assertTrue(
            self.profile1.ledger_entries.filter(year=2025, amount=25).exists())

    def test_get_vacation_balance_with_debits(self):
        """
        Test that the balance is correctly calculated after a debit.
        """
        # Manually create a debit transaction
        absence_service.record_transaction(self.profile1, 2025, -5,
                                           "Test Debit")
        balance = absence_service.get_vacation_balance(self.profile1, 2025)
        self.assertEqual(balance, 20)  # 25 (allowance) - 5 (debit)

    # --- Test Cases for validate_and_debit_absence_request ---

    def test_validation_succeeds_with_sufficient_balance(self):
        """
        Test that a valid request with enough balance passes validation and
        creates a debit.
        """
        request = AbsenceRequest.objects.create(
            employee=self.employee1, start_date=date(2025, 2, 3),
            end_date=date(2025, 2, 7)  # 5 business days
        )
        # This should run without raising an exception
        absence_service.validate_and_debit_absence_request(
            self.profile1, request.start_date, request.end_date, request
        )
        # Check the balance after the debit
        balance = absence_service.get_vacation_balance(self.profile1, 2025)
        self.assertEqual(balance, 20)

    def test_validation_fails_with_insufficient_balance(self):
        """
        Test that a request for more days than available raises a
        ValidationError.
        """
        # Set the balance to 5 days
        absence_service.record_transaction(self.profile1, 2025, -20,
                                           "Prior Debits")

        request = AbsenceRequest.objects.create(
            employee=self.employee1, start_date=date(2025, 3, 3),
            end_date=date(2025, 3, 10)  # 6 business days
        )

        # Use assertRaises to confirm that the expected exception is thrown
        with self.assertRaises(ValidationError) as cm:
            absence_service.validate_and_debit_absence_request(
                self.profile1, request.start_date, request.end_date, request
            )
        # Check the error message
        self.assertIn("Insufficient vacation balance", str(cm.exception))

    def test_validation_fails_on_overlapping_request(self):
        """
        Test that a request that overlaps with an existing one is rejected.
        """
        # Create a pre-existing approved request
        AbsenceRequest.objects.create(
            employee=self.employee1,
            start_date=date(2025, 5, 5),
            end_date=date(2025, 5, 9),
            status=AbsenceRequest.Status.APPROVED
        )

        # Create a new request that overlaps
        overlapping_request = AbsenceRequest.objects.create(
            employee=self.employee1, start_date=date(2025, 5, 7),
            end_date=date(2025, 5, 12)
        )

        with self.assertRaises(ValidationError) as cm:
            absence_service.validate_and_debit_absence_request(
                self.profile1, overlapping_request.start_date,
                overlapping_request.end_date, overlapping_request
            )

        self.assertIn("overlaps with an existing absence request",
                      str(cm.exception))

    def test_validation_succeeds_with_adjacent_requests(self):
        """
        Test that requests that are back-to-back but not overlapping are
        allowed.
        """
        AbsenceRequest.objects.create(
            employee=self.employee1,
            start_date=date(2025, 6, 2),
            end_date=date(2025, 6, 6),
            status=AbsenceRequest.Status.APPROVED
        )

        adjacent_request = AbsenceRequest.objects.create(
            employee=self.employee1, start_date=date(2025, 6, 9),
            end_date=date(2025, 6, 13)
        )

        # This should not raise an exception
        absence_service.validate_and_debit_absence_request(
            self.profile1, adjacent_request.start_date,
            adjacent_request.end_date, adjacent_request
        )
        self.assertEqual(AbsenceRequest.objects.count(), 2)

    # --- Test Cases for Multi-Year Requests ---

    def test_multi_year_request_debits_correctly_across_years(self):
        """
        Test that a request spanning two years debits the correct number of
        days from each year's balance.
        """
        # Request from Dec 30, 2025 to Jan 3, 2026
        # 2025: Dec 30, 31 (2 business days)
        # 2026: Jan 2 (1 business days, Jan 1 is a holiday, Jan 3 is a Saturday)
        request = AbsenceRequest.objects.create(
            employee=self.employee1, start_date=date(2025, 12, 30),
            end_date=date(2026, 1, 3)
        )

        absence_service.validate_and_debit_absence_request(
            self.profile1, request.start_date, request.end_date, request
        )

        # Check 2025 balance
        balance_2025 = absence_service.get_vacation_balance(self.profile1, 2025)
        self.assertEqual(balance_2025, 23)  # 25 - 2 days

        # Check 2026 balance
        balance_2026 = absence_service.get_vacation_balance(self.profile1, 2026)
        self.assertEqual(balance_2026, 24)  # 25 - 1 days

    def test_multi_year_request_fails_if_second_year_has_insufficient_balance(
            self):
        """
        Test that a multi-year request fails if the balance for the second
        year is insufficient.
        """
        # Give the user only 1 day of vacation in 2026
        absence_service.record_transaction(self.profile1, 2026, -24,
                                           "Prior Debits 2026")

        request = AbsenceRequest.objects.create(
            employee=self.employee1, start_date=date(2025, 12, 30),
            end_date=date(2026, 1, 8)
        )

        with self.assertRaises(ValidationError) as cm:
            absence_service.validate_and_debit_absence_request(
                self.profile1, request.start_date, request.end_date, request
            )
        self.assertIn("Insufficient vacation balance.",
                      str(cm.exception))

    # --- Test Cases for handle_absence_status_update
    # (Permissions are tested at the View level) ---
    
    def test_rejecting_request_credits_ledger(self):
        """
        Test that changing a request's status to REJECTED creates a credit
        transaction.
        """
        request = AbsenceRequest.objects.create(
            employee=self.employee1, start_date=date(2025, 7, 7),
            end_date=date(2025, 7, 11)  # 5 days
        )
        # Initial debit
        absence_service.validate_and_debit_absence_request(
            self.profile1, request.start_date, request.end_date, request
        )
        self.assertEqual(
            absence_service.get_vacation_balance(self.profile1, 2025), 20)

        # Manager rejects the request
        absence_service.handle_absence_status_change(request,
                                                     AbsenceRequest.Status.REJECTED)

        # Balance should be restored
        self.assertEqual(
            absence_service.get_vacation_balance(self.profile1, 2025), 25)
        # Check that the request status is updated
        self.assertEqual(request.status, AbsenceRequest.Status.REJECTED)
