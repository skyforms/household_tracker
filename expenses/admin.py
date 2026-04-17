from django.contrib import admin
from .models import (
    Month,
    Deposit,
    Purchase,
    UserProfile,
    UtilityBill,
    UtilityShare
)

admin.site.register(Month)
admin.site.register(Deposit)
admin.site.register(Purchase)
admin.site.register(UserProfile)
admin.site.register(UtilityBill)
admin.site.register(UtilityShare)
