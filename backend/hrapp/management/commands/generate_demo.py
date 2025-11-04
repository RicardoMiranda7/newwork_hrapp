from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from hrapp.models import Profile
from datetime import datetime, date

class Command(BaseCommand):
    help = 'Generates demo data for the application'

    def handle(self, *args, **kwargs):
        User = get_user_model()

        # 1. Create manager user
        manager, created = User.objects.get_or_create(
            email="manager@example.com",
            defaults={
                'username': 'manager',
                'is_active': True,
            }
        )
        if created:
            manager.set_password('password123')
            manager.save()

        # 2. Create employee user and profile
        employee, created = User.objects.get_or_create(
            email="john.smith@example.com",
            defaults={
                'username': 'johnsmith',
                'is_active': True,
            }
        )
        if created:
            employee.set_password('password123')
            employee.save()

        # Create and link profile for John Smith
        profile, created = Profile.objects.get_or_create(
            user=employee,
            defaults={
                'full_name': 'John Smith',
                'job_title': 'Software Developer',
                'salary': 75000.00,
                'gender': 'Male',
                'date_of_birth': date(1990, 1, 1),
                'address': '123 Main St, City',
                'phone_number': '555-0123',
                'bio': 'Experienced software developer',
                'joined_at': datetime.now(),
                'department': 'Engineering',
                'manager': manager
            }
        )

        # 3. Create co-worker user
        coworker, created = User.objects.get_or_create(
            email="john.doe@example.com",
            defaults={
                'username': 'johndoe',
                'is_active': True,
            }
        )
        if created:
            coworker.set_password('password123')
            coworker.save()

        # Create and link profile for John Smith
        profile, created = Profile.objects.get_or_create(
            user=coworker,
            defaults={
                'full_name': 'John Doe',
                'job_title': 'Business Analyst',
                'salary': 75000.00,
                'gender': 'Male',
                'date_of_birth': date(1990, 1, 1),
                'address': '123 Main St, City',
                'phone_number': '555-0123',
                'bio': 'Experienced business analyst',
                'joined_at': datetime.now(),
                'department': 'Business',
                'manager': manager
            }
        )

        self.stdout.write(self.style.SUCCESS('Demo data generated successfully!'))
