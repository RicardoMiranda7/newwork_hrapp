from datetime import date, timedelta

from django.db.models import Sum

from hrapp.models import AbsenceRequest, Profile, AbsenceLedger

# --- CONFIGURATION ---
YEARLY_VACATION_ALLOWANCE = 25


def validate_and_debit_absence_request(profile: Profile, start_date: date,
                                       end_date: date, request: AbsenceRequest):
    year = start_date.year
    requested_days = end_date - start_date + timedelta(days=1)

    record_transaction(
        profile=profile,
        year=year,
        amount=-requested_days.days,  # Debit is a negative amount
        description=f"Absence request submitted ({request.start_date} to "
                    f"{request.end_date})",
        request=request
    )


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
        absence_request=request
    )
