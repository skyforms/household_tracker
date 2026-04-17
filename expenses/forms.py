from django import forms
from django.contrib.auth.models import User
from .models import UtilityBill, Month


class UtilityBillForm(forms.ModelForm):
    """
    Form for adding a new utility bill.
    This form only handles the bill itself — the splitting logic
    will be triggered in the view after the bill is saved.
    """

    class Meta:
        model = UtilityBill
        fields = ["bill_type", "amount", "month", "billing_period", "paid_by"]

        # Add labels to make the form user-friendly
        labels = {
            "bill_type": "Utility Type",
            "amount": "Total Amount",
            "month": "Month (Bill Arrived)",
            "billing_period": "Billing Period (optional)",
            "paid_by": "Paid By",
        }

        # Add widgets to improve the UI
        widgets = {
            "bill_type": forms.Select(attrs={"class": "form-select"}),
            "amount": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "month": forms.Select(attrs={"class": "form-select"}),
            "billing_period": forms.TextInput(attrs={"class": "form-control"}),
            "paid_by": forms.Select(attrs={"class": "form-select"}),
        }

    # ----------------------------------------------------------
    # Helper: override __init__ to customize dropdown behavior
    # ----------------------------------------------------------
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Sort months by date (optional but nice)
        self.fields["month"].queryset = Month.objects.order_by("start_date")

        # Filter users to household members only
        self.fields["paid_by"].queryset = User.objects.filter(
            userprofile__is_household_member=True
        ).order_by("username")

        # Optional: set default payer to Jade if she exists
        try:
            jade = User.objects.get(username="jade")
            self.fields["paid_by"].initial = jade.id
        except User.DoesNotExist:
            pass

    # ----------------------------------------------------------
    # Helper: clean the billing period text
    # ----------------------------------------------------------
    def clean_billing_period(self):
        """
        Normalize the billing period text.
        Example: 'march-april' → 'March–April'
        """
        period = self.cleaned_data.get("billing_period", "").strip()

        if period == "":
            return period

        # Capitalize each word
        period = period.title()

        # Replace hyphens with an en dash
        period = period.replace("-", "–")

        return period
