from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save


class Month(models.Model):
    name = models.CharField(max_length=20, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.name

class Deposit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.ForeignKey(Month, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} deposited {self.amount}"

class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.ForeignKey(Month, on_delete=models.CASCADE)
    item = models.CharField(max_length=100)
    brand = models.CharField(max_length=100, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.item} ({self.brand}) - {self.price}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_household_member = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

class UtilityBill(models.Model):
    """
    Represents a single utility bill (Gas, Electricity, Water, Internet).
    This stores the total amount Jade paid, the month it arrived,
    and the billing period (e.g., 'March–April') for historical accuracy.
    """

    BILL_TYPES = [
        ("gas", "Gas"),
        ("electricity", "Electricity"),
        ("water", "Water"),
        ("internet", "Internet"),
    ]

    bill_type = models.CharField(
        max_length=20,
        choices=BILL_TYPES,
        help_text="Type of utility bill (Gas, Electricity, Water, Internet)."
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Total amount of the bill."
    )

    # Month the bill is assigned to (the month it ARRIVED)
    month = models.ForeignKey(
        Month,
        on_delete=models.CASCADE,
        help_text="Month the bill arrived (not necessarily the usage month)."
    )

    # Optional: store the real billing period (e.g., 'March–April')
    billing_period = models.CharField(
        max_length=50,
        blank=True,
        help_text="Actual billing period (e.g., 'March–April')."
    )

    # Who paid the bill (usually Jade)
    paid_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="Person who paid the bill upfront."
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_bill_type_display()} - {self.month.name}"

    # -----------------------------
    # Helper Methods
    # -----------------------------

    def split_evenly(self, users):
        """
        Automatically split the bill evenly among all users.
        Creates UtilityShare objects for each person.
        Jade (paid_by) is automatically marked as paid.
        """
        per_person = self.amount / len(users)

        for user in users:
            UtilityShare.objects.create(
                bill=self,
                user=user,
                amount_owed=per_person,
                has_paid=(user == self.paid_by)  # Jade is auto-marked as paid
            )

    def total_paid(self):
        """Return the total amount already paid back to Jade."""
        return sum(share.amount_owed for share in self.shares.filter(has_paid=True))

    def total_unpaid(self):
        """Return the total amount still owed to Jade."""
        return sum(share.amount_owed for share in self.shares.filter(has_paid=False))
    

class UtilityShare(models.Model):
    """
    Represents each person's share of a utility bill.
    Tracks how much they owe and whether they have paid Jade back.
    """

    bill = models.ForeignKey(
        UtilityBill,
        on_delete=models.CASCADE,
        related_name="shares"
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    amount_owed = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Amount this person owes for the bill."
    )

    has_paid = models.BooleanField(
        default=False,
        help_text="Has this person paid Jade back?"
    )

    def __str__(self):
        return f"{self.user.username} owes {self.amount_owed} for {self.bill}"

    # -----------------------------
    # Helper Methods
    # -----------------------------

    def mark_paid(self):
        """Mark this share as paid."""
        self.has_paid = True
        self.save()

    def mark_unpaid(self):
        """Mark this share as unpaid."""
        self.has_paid = False
        self.save()

