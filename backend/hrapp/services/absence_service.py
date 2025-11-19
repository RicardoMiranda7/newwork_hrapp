from datetime import date, timedelta
from typing import Set

import numpy as np
from django.db.models import Sum
from rest_framework.exceptions import ValidationError

from hrapp.models import BankHoliday, AbsenceRequest, Profile, AbsenceLedger

# --- CONFIGURATION ---
YEARLY_VACATION_ALLOWANCE = 25


def get_bank_holidays_for_year(year: int) -> Set[date]:
    """
    Fetches all bank holidays for a given year from the database.
    Using a set provides fast O(1) average time complexity for lookups.
    """
    return set(BankHoliday.objects.filter(date__year=year).values_list('date',
                                                                       flat=True))


def get_vacation_balance(profile: Profile, year: int) -> int:
    """
    Calculates the vacation balance for a profile and year by summing ledger
    entries.
    """
    # Check if the initial allowance has been granted for the year. If not,
    # grant it.
    if not profile.ledger_entries.filter(year=year,
                                         description="Yearly "
                                                     "Allowance").exists():
        record_transaction(profile, year, YEARLY_VACATION_ALLOWANCE,
                           "Yearly Allowance")

    # Sum all transaction amounts for the given year.
    balance_agg = profile.ledger_entries.filter(year=year).aggregate(
        balance=Sum('amount'))
    return balance_agg['balance'] or 0


def record_transaction(profile: Profile, year: int, amount: int,
                       description: str, request: AbsenceRequest = None):
    """Creates a new entry in the AbsenceLedger."""
    AbsenceLedger.objects.create(
        profile=profile,
        year=year,
        amount=amount,
        description=description,
        absence_request=request)


def calculate_business_days(start_date: date, end_date: date,
                            holidays: Set[date]) -> int:
    """
    Calculates the number of business days between two dates with high
    efficiency.
    This algorithm uses numpy's `busday_count` which is significantly faster
    than iterating day by day.

    Args:
        start_date: The start date of the period.
        end_date: The end date of the period.
        holidays: A set of bank holiday dates to exclude.

    Returns:
        The total number of business days.
    """
    # numpy's busday_count is exclusive of the end date, so we add one day to
    # make it inclusive.
    inclusive_end_date = end_date + timedelta(days=1)

    # Convert holiday set to a list of strings, which is the format numpy
    # expects.
    holiday_list = [h.strftime('%Y-%m-%d') for h in holidays]

    # Calculate the number of weekdays (Mon-Fri) between the dates.
    # The result is an array, so we extract the single value with .item().
    business_days = np.busday_count(
        start_date.strftime('%Y-%m-%d'),
        inclusive_end_date.strftime('%Y-%m-%d'),
        holidays=holiday_list
    ).item()

    return business_days


def validate_and_debit_absence_request(profile: Profile, start_date: date,
                                       end_date: date, request: AbsenceRequest):
    """
    Validates an absence request against the employee's vacation balance and
    other vacation periods

    Args:
        profile: The employee's profile.
        start_date: The start date of the absence.
        end_date: The end date of the absence.
        request: The AbsenceRequest instance being processed.

    Returns:
        None. If validation passes, a debit transaction is recorded.

    Raises:
        ValidationError: If there are insufficient vacation days or if there are
        overlapping absence requests.
    """

    # Basic date validation.
    if start_date > end_date:
        raise ValidationError(
            "The start date must be before or equal to the end date.")

    # Check for intersecting absence requests (exclude itself).
    # Raise error if any exist.
    intersection = AbsenceRequest.objects.filter(
        employee=profile.user,
        status__in=[AbsenceRequest.Status.PENDING,
                    AbsenceRequest.Status.APPROVED],
        start_date__lte=end_date,
        end_date__gte=start_date
    ).exclude(id=request.id)
    if intersection.exists():
        raise ValidationError(
            "The requested absence period overlaps with an existing "
            "absence request.")

    # When multi-year absences are requested, split the validation and debit
    # across the years.
    for year in range(start_date.year, end_date.year + 1):
        # Determine the start and end dates for this year segment.
        segment_start_date = max(start_date, date(year, 1, 1))
        segment_end_date = min(end_date, date(year, 12, 31))

        # Fetch current vacation balance and raise error if zero or negative.
        current_balance = get_vacation_balance(profile, year)
        if current_balance <= 0:
            raise ValidationError(
                "You have no remaining vacation days for this year.")

        # Fetch bank holidays for the year.
        holidays = get_bank_holidays_for_year(year)
        # Calculate the number of business days in the requested period.
        requested_days = calculate_business_days(segment_start_date,
                                                 segment_end_date, holidays)

        if requested_days <= 0:
            raise ValidationError(
                "The selected date range contains no business days.")

        if requested_days > current_balance:
            raise ValidationError(
                f"Insufficient vacation balance. You have {current_balance} "
                f"days remaining, but this request is for {requested_days} "
                f"business days.")

        # If validation passes, record the debit transaction.
        record_transaction(
            profile=profile,
            year=year,
            amount=-requested_days,  # Debit is a negative amount
            description=f"Absence request submitted ({request.start_date} to "
                        f"{request.end_date})",
            request=request)


def handle_absence_status_change(request: AbsenceRequest, new_status: str):
    """
    Handles the logic for changing the status of an absence request,
    including updating ledger entries as needed.
    Designed to be called within a transaction.

    Args:
        request: The AbsenceRequest instance being updated.
        new_status: The new status to set.

    Returns:
        None. The request is updated in place.
    """
    # When multi-year absence, split the validation and update across the years
    for year in range(request.start_date.year, request.end_date.year + 1):
        if (new_status == AbsenceRequest.Status.REJECTED and request.status !=
                AbsenceRequest.Status.REJECTED):
            # Find the original debit transaction and refund it.
            original_debit = request.ledger_entries.filter(amount__lt=0,
                                                           year=year).first()
            if original_debit:
                record_transaction(
                    profile=request.employee.profile,
                    year=original_debit.year,
                    amount=-original_debit.amount,
                    # Credit back the positive amount
                    description=f"Absence request rejected",
                    request=request
                )
        # If a rejected request is moved back to PENDING or APPROVED, we need to
        # re-debit.
        elif (request.status == AbsenceRequest.Status.REJECTED and new_status !=
              AbsenceRequest.Status.APPROVED):
            # Find the original credit transaction and re-debit it.
            original_credit = request.ledger_entries.filter(amount__gt=0,
                                                            year=year).first()
            record_transaction(
                profile=request.employee.profile,
                year=original_credit.year,
                amount=-original_credit.amount,
                description=f"Absence request re-opened ({new_status})",
                request=request
            )
    request.status = new_status
    request.save()
