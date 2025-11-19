from django.contrib import admin

from .models import User, Profile, Feedback, AbsenceRequest, AbsenceLedger, \
    BankHoliday

# All models are registered for admin interface
admin.site.register(User)
admin.site.register(Profile)
admin.site.register(Feedback)
admin.site.register(AbsenceRequest)
admin.site.register(AbsenceLedger)
admin.site.register(BankHoliday)