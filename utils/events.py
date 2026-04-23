from datetime import date

def select_week_dates(selected_date):
    """Returns the start date and end date of the week based on selected date object"""
    # Get the week number of the date
    week_num = selected_date.isocalendar()[1]

    # Checking for the condition when week 53 spans into the next year
    if week_num == 53 and selected_date.month == 1:
        year = selected_date.year - 1
    else:
        year = selected_date.year
    
    # Start date and end date of the week based on selected date
    start_date = date.fromisocalendar(year, week_num, 1)
    end_date = date.fromisocalendar(year, week_num, 7)

    return start_date, end_date

