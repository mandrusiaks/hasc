from datetime import datetime, date

def get_todays_midnight():
    today = date.today()
    return datetime.combine(today, datetime.min.time())
