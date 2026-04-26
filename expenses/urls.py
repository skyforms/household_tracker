from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("deposit/", views.add_deposit, name="add_deposit"),
    path("purchase/", views.add_purchase, name="add_purchase"),
    path("summary/<int:month_id>/", views.month_summary, name="month_summary"),

    # Bills home
    path("bills/", views.bills_home, name="bills_home"),

    # Utilities
    path("bills/utilities/add/", views.add_utility_bill, name="add_utility_bill"),
    path("bills/utilities/", views.utilities_dashboard, name="utilities_dashboard"),
    path("bills/utilities/toggle/<int:share_id>/", views.toggle_utility_payment, name="toggle_utility_payment"),
    path("bills/utilities/summary/<int:month_id>/", views.utilities_monthly_summary, name="utilities_monthly_summary"),
    path("bills/utilities/<int:bill_id>/delete/", views.delete_utility_bill, name="delete_utility_bill"),
    path("bills/utilities/<int:bill_id>/edit/", views.edit_utility_bill, name="edit_utility_bill"),
]
