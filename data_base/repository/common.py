from datetime import date, timedelta


def fst_day_of_this_month():
    """Return the date for the first day of entered month"""
    today_date = date.today()
    return date(today_date.year, today_date.month, 1)


def fst_day_of_next_month() -> str:
    """Based on the current date, return the date for the first day of the next month"""
    date_ = date.today()
    month = date_.month
    while month == date_.month:
        date_ = date_ + timedelta(days=1)
        if month != date_.month:
            return date_
