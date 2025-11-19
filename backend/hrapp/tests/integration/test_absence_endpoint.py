from datetime import date

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from hrapp.models import Profile, AbsenceRequest, BankHoliday
from hrapp.serializers import AbsenceRequestSerializer
from hrapp.services import absence_service

User = get_user_model()


class AbsenceRequestEndpointTestCase(APITestCase):
    """
    Integration test suite for the /api/v1/absences/ endpoint.
    This tests the full request-response cycle, including permissions,
    serialization, and view logic.
    """
    client: APIClient

    @classmethod
    def setUpTestData(cls):
        """
        Set up non-modified objects used by all test methods.
        setUpTestData is executed once for the entire test class.
        This is the ideal place to create users, profiles, and other
        foundational data to ensure perfect test isolation.
        """
        # Create Users
        cls.manager_user = User.objects.create_user(
            username='manager', email='manager@example.com',
            password='password123'
        )
        cls.employee1_user = User.objects.create_user(
            username='employee1', email='employee1@example.com',
            password='password123'
        )
        cls.employee2_user = User.objects.create_user(
            username='employee2', email='employee2@example.com',
            password='password123'
        )

        # Create Profiles for ALL users.
        cls.manager_profile = Profile.objects.create(
            user=cls.manager_user, full_name="Manager User", manager=None
        )
        cls.employee1_profile = Profile.objects.create(
            user=cls.employee1_user, full_name="Employee One",
            manager=cls.manager_user
        )
        cls.employee2_profile = Profile.objects.create(
            user=cls.employee2_user, full_name="Employee Two",
            manager=cls.manager_user
        )

        # Create Bank Holidays
        BankHoliday.objects.create(name="Holiday", date=date(2025, 5, 26))

        # Define URLs
        cls.list_create_url = reverse('absencerequest-list')

    def setUp(self):
        """
        This method now runs after setUpTestData.
        It's the perfect place for things that might change in each test,
        like authenticating a client.
        """
        # Placeholder for now.
        pass

    # --- Test Case: Absence Creation ---

    def test_authenticated_employee_can_create_valid_request(self):
        """
        Verify that a logged-in employee can successfully submit a valid
        absence request.
        """
        # Authenticate the client as employee1
        self.client.force_authenticate(user=self.employee1_user)

        request_data = {
            "start_date": "2025-06-02",
            "end_date": "2025-06-06",
            "reason": "Annual leave"
        }

        response = self.client.post(self.list_create_url, request_data,
                                    format='json')

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AbsenceRequest.objects.count(), 1)
        self.assertEqual(AbsenceRequest.objects.first().employee,
                         self.employee1_user)
        # Verify that the ledger was debited
        balance = absence_service.get_vacation_balance(self.employee1_profile, 2025)
        self.assertEqual(balance, 20)  # 25 allowance - 5 days

    def test_create_request_fails_with_insufficient_balance(self):
        """
        Verify that the API returns a 400 Bad Request if the user's balance
        is too low.
        """
        # Manually set the employee's balance to 3 days
        absence_service.record_transaction(self.employee1_profile, 2025, -22,
                                           "Prior Debits")

        self.client.force_authenticate(user=self.employee1_user)
        request_data = {
            "start_date": "2025-07-07",  # Requesting 5 days
            "end_date": "2025-07-11",
            "reason": "Trip"
        }

        response = self.client.post(self.list_create_url, request_data,
                                    format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Insufficient vacation balance", str(response.data))
        self.assertEqual(AbsenceRequest.objects.count(),
                         0)  # Ensure nothing was created

    def test_unauthenticated_user_cannot_create_request(self):
        """
        Verify that unauthenticated requests are rejected with a 401
        Unauthorized.
        """
        request_data = {"start_date": "2025-06-02", "end_date": "2025-06-06",
                        "reason": "Should fail"}
        response = self.client.post(self.list_create_url, request_data,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- Test Case: Absence Listing (Permissions) ---

    def test_employee_can_see_others_approved_absences(self):
        """
        Verify that the list endpoint returns all approved absence requests from other employees (since vacations are public)
        """
        # Create requests for two different employees
        request1 = AbsenceRequest.objects.create(employee=self.employee1_user,
                                                 start_date=date(2025, 8, 4),
                                                 end_date=date(2025, 8, 8),
                                                 status=AbsenceRequest.Status.PENDING)
        request2 = AbsenceRequest.objects.create(employee=self.employee2_user,
                                                 start_date=date(2025, 9, 1),
                                                 end_date=date(2025, 9, 5),
                                                 status=AbsenceRequest.Status.APPROVED)

        self.client.force_authenticate(user=self.employee1_user)
        response = self.client.get(self.list_create_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Should see 2 requests

    def test_employee_can_see_all_own_absences(self):
        """
        Verify that the list endpoint returns all approved absence requests from other employees (since vacations are public)
        """
        # Create requests for two different employees
        request1 = AbsenceRequest.objects.create(employee=self.employee1_user,
                                                 start_date=date(2025, 8, 4),
                                                 end_date=date(2025, 8, 8),
                                                 status=AbsenceRequest.Status.PENDING)
        request2 = AbsenceRequest.objects.create(employee=self.employee1_user,
                                                 start_date=date(2025, 10, 1),
                                                 end_date=date(2025, 10, 5),
                                                 status=AbsenceRequest.Status.APPROVED)
        request3 = AbsenceRequest.objects.create(employee=self.employee2_user,
                                                 start_date=date(2025, 11, 1),
                                                 end_date=date(2025, 11, 5),
                                                 status=AbsenceRequest.Status.PENDING)

        self.client.force_authenticate(user=self.employee1_user)
        response = self.client.get(self.list_create_url)

        self.assertEqual(len(response.data), 2)  # Should see 2 requests
        self.assertTrue(response.data[0]["employee"]==self.employee1_user.email)
        self.assertTrue(response.data[1]["employee"]==self.employee1_user.email)


    # --- Test Case: Status Update (Permissions) ---

    def test_manager_can_approve_a_request(self):
        """
        Verify that a manager can successfully update the status of a team
        member's request.
        """
        absence = AbsenceRequest.objects.create(employee=self.employee1_user,
                                                start_date=date(2025, 10, 6),
                                                end_date=date(2025, 10, 10),
                                                reason="Annual leave")
        # 'absencerequest-update-status' is the default name for a custom
        # action on a ViewSet
        update_url = reverse('absencerequest-update-status')

        self.client.force_authenticate(user=self.manager_user)
        request_data = {
            "id": absence.id,
            "employee": "employee1@example.com",
            "start_date": "2025-10-06",
            "end_date": "2025-10-10",
            "reason": "Annual leave",
            "status": "APPROVED"
        }
        response = self.client.patch(update_url, request_data, format='json')

        # Assert HTTP status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert db object
        absence.refresh_from_db()  # Reload the object from the database
        self.assertEqual(absence.status, AbsenceRequest.Status.APPROVED)

        # Assert that the response data matches the updated object
        expected_data = AbsenceRequestSerializer(response.data).data
        self.assertEqual(expected_data, AbsenceRequestSerializer(request_data).data)

    def test_employee_cannot_approve_their_own_request(self):
        """
        Verify that a non-manager receives a 403 Forbidden when trying to
        update status.
        """
        absence = AbsenceRequest.objects.create(employee=self.employee1_user,
                                                start_date=date(2025, 11, 3),
                                                end_date=date(2025, 11, 7))
        update_url = reverse('absencerequest-update-status')
        request_data = {
            "id": absence.id,
            "employee": "employee1@example.com",
            "start_date": "2025-11-03",
            "end_date": "2025-11-07",
            "reason": "",
            "status": "APPROVED"
        }
        # Authenticate as the employee themselves, not the manager
        self.client.force_authenticate(user=self.employee1_user)
        response = self.client.patch(update_url, request_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
