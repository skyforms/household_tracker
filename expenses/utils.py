from datetime import date
import calendar
from .models import Month

def get_or_create_current_month():
    today = date.today()
    month_name = today.strftime("%Y-%m")

    start_date = today.replace(day=1)
    last_day = calendar.monthrange(today.year, today.month)[1]
    end_date = today.replace(day=last_day)

    month, created = Month.objects.get_or_create(
        name=month_name,
        defaults={
            "start_date": start_date,
            "end_date": end_date
        }
    )
    return month
