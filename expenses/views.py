from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum
from .models import Deposit, Purchase, Month, UtilityBill, UtilityShare
from .utils import get_or_create_current_month
from .forms import UtilityBillForm

def dashboard(request):
    month = get_or_create_current_month()
    deposits_total = Deposit.objects.filter(month=month).aggregate(Sum("amount"))["amount__sum"] or 0
    purchases_total = Purchase.objects.filter(month=month).aggregate(Sum("price"))["price__sum"] or 0
    balance = deposits_total - purchases_total
    recent_purchases = Purchase.objects.filter(month=month).order_by('-date')[:20]

    return render(request, "expenses/dashboard.html", {
        "month": month,
        "deposits_total": deposits_total,
        "purchases_total": purchases_total,
        "balance": balance,
        "recent_purchases": recent_purchases,
    })

def add_deposit(request):
    month = get_or_create_current_month()
    users = User.objects.filter(userprofile__is_household_member=True)

    if request.method == "POST":
        Deposit.objects.create(
            user=User.objects.get(id=request.POST["user"]),
            month=month,
            amount=request.POST["amount"],
        )
        return redirect("dashboard")

    return render(request, "expenses/deposits.html", {
        "month": month,
        "users": users,
    })

def add_purchase(request):
    month = get_or_create_current_month()
    users = User.objects.filter(userprofile__is_household_member=True)

    if request.method == "POST":
        Purchase.objects.create(
            user=User.objects.get(id=request.POST["user"]),
            month=month,
            item=request.POST["item"],
            brand=request.POST["brand"],
            price=request.POST["price"],
        )
        return redirect("dashboard")

    return render(request, "expenses/purchases.html", {
        "month": month,
        "users": users,
    })

def month_summary(request, month_id):
    month = Month.objects.get(id=month_id)
    users = User.objects.filter(userprofile__is_household_member=True)

    summary = []
    for u in users:
        deposits = Deposit.objects.filter(month=month, user=u).aggregate(Sum("amount"))["amount__sum"] or 0
        purchases = Purchase.objects.filter(month=month, user=u).aggregate(Sum("price"))["price__sum"] or 0
        summary.append({
            "user": u,
            "deposits": deposits,
            "purchases": purchases,
            "net": deposits - purchases,
        })

    return render(request, "expenses/month_summary.html", {
        "month": month,
        "summary": summary,
    })


def bills_home(request):
    return render(request, "expenses/bills_home.html")

def add_utility_bill(request):
    """
    View for adding a new utility bill.
    - Shows the form
    - Saves the bill
    - Automatically splits the bill evenly among all users
    - Marks Jade (paid_by) as paid
    """

    if request.method == "POST":
        form = UtilityBillForm(request.POST)

        if form.is_valid():
            # Save the bill itself
            bill = form.save()

            # Get all users in the system (Mara, Donnie, Jade)
            users = User.objects.filter(userprofile__is_household_member=True)

            # Use the helper method in the model to split the bill
            bill.split_evenly(users)

            messages.success(request, "Utility bill added and split successfully!")
            return redirect("utilities_dashboard")

    else:
        form = UtilityBillForm()

    return render(request, "expenses/utilities/add_utility_bill.html", {"form": form})

def utilities_dashboard(request):
    """
    Shows all utility bills for the current month.
    Displays each person's share and allows toggling paid/unpaid.
    """

    month = get_or_create_current_month()

    # Get all bills for this month
    bills = UtilityBill.objects.filter(month=month).order_by("-created_at")

    return render(request, "expenses/utilities/utilities_dashboard.html", {
        "month": month,
        "bills": bills,
    })

def toggle_utility_payment(request, share_id):
    """
    Toggle the paid/unpaid status for a specific UtilityShare entry.
    This allows Jade (or anyone) to mark payments as received.
    """

    share = UtilityShare.objects.get(id=share_id)

    # Flip the boolean
    share.has_paid = not share.has_paid
    share.save()

    messages.success(request, f"Updated payment status for {share.user.username}.")
    return redirect("utilities_dashboard")

def utilities_monthly_summary(request, month_id):
    """
    Monthly summary of all utility bills for a given month.
    Shows:
    - Total utilities
    - Per-person totals
    - How much each person has paid
    - How much each person still owes
    """

    month = Month.objects.get(id=month_id)
    users = User.objects.filter(userprofile__is_household_member=True)

    # All bills for this month
    bills = UtilityBill.objects.filter(month=month)

    # All shares for this month
    shares = UtilityShare.objects.filter(bill__month=month)

    # Prepare per-person summary
    summary = []

    for user in users:
        user_shares = shares.filter(user=user)

        total_owed = sum(s.amount_owed for s in user_shares)
        total_paid = sum(s.amount_owed for s in user_shares if s.has_paid)
        total_unpaid = total_owed - total_paid

        summary.append({
            "user": user,
            "total_owed": total_owed,
            "total_paid": total_paid,
            "total_unpaid": total_unpaid,
        })

    # Total utilities for the month
    total_utilities = sum(b.amount for b in bills)

    return render(request, "expenses/utilities/monthly_summary.html", {
        "month": month,
        "bills": bills,
        "summary": summary,
        "total_utilities": total_utilities,
    })


