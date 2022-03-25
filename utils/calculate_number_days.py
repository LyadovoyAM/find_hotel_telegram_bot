import datetime


def calculate_days(arrival_date: str, date_departure: str) -> int:
    """Считает количество дней из дат введенных пользователем"""
    pattern = '%Y-%m-%d'
    day_1 = datetime.datetime.strptime(arrival_date, pattern)
    day_2 = datetime.datetime.strptime(date_departure, pattern)
    result = day_2 - day_1
    number_days = result.days
    return number_days
