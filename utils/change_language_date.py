def change_language_date(text: str) -> str:
    """Находит и меняет в тексте слова year, month, day на русские"""
    dates = {'year': 'год', 'month': 'месяц', 'day': 'день'}
    for date in dates.keys():
        if text.find(date) != -1:
            new_text = text.replace(date, dates[date])
            return new_text
