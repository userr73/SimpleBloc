from datetime import date, timedelta, time

from utils.db import get_db, query_all, query_one

def get_todays_events(user_id):
    """Retrieve the user's events for the day."""
    sql = '''
        SELECT start_time, end_time, event_title
        FROM Events
        WHERE event_date = ? AND user_id = ?
    '''

    data = (
        date.today(),
        user_id
    )

    events = query_all(sql, data)

    return events

def get_overlapping_events(user_id, input_date, start_time, end_time):
    """Retrieves the user's overlapping events on a given day, filtered with the start and end time to determine any overlapping events."""
    sql = '''
        SELECT start_time, end_time, event_title
        FROM Events
        WHERE event_date = ? AND user_id = ?
    '''

    data = (input_date, user_id)
    
    events = query_all(sql, data)
    overlaps = []

    for event in events:
        event = dict(event)
        existing_start_time = time.fromisoformat(event['start_time'])
        existing_end_time = time.fromisoformat(event['end_time'])

        if existing_start_time < start_time and existing_end_time > start_time:
            overlaps.append(event['event_title'])
        elif existing_start_time >= start_time and existing_start_time < end_time:
            overlaps.append(event['event_title'])
    
    return overlaps


def get_all_user_custom_categories(user_id):
    """Retrieve all the user's categories except for the default category"""
    sql = '''
        SELECT *
        FROM Categories 
        WHERE user_id = ? AND category_name != ?
    '''

    data = (
        user_id,
        'No category'
    )
    categories = query_all(sql, data)

    return categories
    

def date_to_local_format(data):
    """Converts an ISO 8601 format date string into a formatted local date"""
    date_obj = date.fromisoformat(data)

    return date_obj.strftime('%x')


def is_default_category(category_id, default_category_name):
    """Checks whether a given category id is the default category (No category). Returns a boolean"""
    sql = '''
        SELECT category_name
        FROM Categories
        WHERE category_id = ?
    '''
    data = (category_id,)
    category_obj = query_one(sql, data)
    category_name = category_obj['category_name']

    # Check whether the category is the default
    if category_name == default_category_name:
        return True
    
    return False


def get_event_details(event_id, user_id):
    """Retrieves the dictionary of event details for a specific event and user"""
    sql = '''
        SELECT *
        FROM Events
        JOIN Categories on Categories.category_id = Events.category_id
        WHERE Events.event_id = ? AND Events.user_id = ?
    '''

    data = (event_id, user_id)
    event_details = query_one(sql, data)

    # Return the category details or None if not found
    return dict(event_details) if event_details else None


def get_category_details(category_id, user_id):
    """Retrieves the dictionary of category details for a specific category and user"""
    sql = '''
        SELECT category_name, category_id
        FROM Categories
        WHERE category_id = ? AND user_id = ?
    '''
    data = (category_id, user_id)
    category_details = query_one(sql, data)

    # Return the category details or None if not found
    return dict(category_details) if category_details else None


def get_this_weeks_days(start_date):
    """Returns the seven dates (day) of the selected week"""
    dates = {}

    for idx, day in enumerate(['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']):
        next_day = start_date + timedelta(days=idx)
        dates[day] = next_day.day
    
    return dates



def time_to_row_num(event_time):
    """Returns the relevant row number of the given time"""
    hr, min = event_time.split(':')

    row_num = int(hr) * 12 + int(int(min) // 5) + 3

    return row_num


def date_to_day_name(event_date):
    """Returns the relevant day of the week name based on the date given"""
    # Convert the date to a date object
    date_obj = date.fromisoformat(event_date)
    
    # Get the day of the week (number)
    day_num = date_obj.isocalendar()[2]
    
    # Match the day number with the relevant column name
    match day_num:
        case 1:
            day_name = 'Monday'
        case 2:
            day_name = 'Tuesday'
        case 3:
            day_name = 'Wednesday'
        case 4:
            day_name = 'Thursday'
        case 5:
            day_name = 'Friday'
        case 6:
            day_name = 'Saturday'
        case 7:
            day_name = 'Sunday'

    return day_name


def get_event_styling(events):
    """Returns a list of dictionaries containing the column name and row start and end values"""
    events_style_ls = []

    for event in events:
        # Get the column name
        col_name = date_to_day_name(event['event_date'])

        # Get the row start and end numbers
        row_start = time_to_row_num(event['start_time'])
        row_end = time_to_row_num(event['end_time'])

        # Determine the border bottom colour
        if row_end % 12 == 3:
            border_bottom_colour = 'rgb(190, 190, 190)'
        else:
            border_bottom_colour = 'transparent'

        # Add these column and row values to a dictionary
        event_dict = {
            'col_name': col_name, 
            'row_start': row_start, 
            'row_end': row_end,
            'border_bottom_colour': border_bottom_colour
        }

        # Add the dictionary as a list item
        events_style_ls.append(event_dict)
    
    return events_style_ls


def get_this_week_events(user_id, start, end):
    """Retrieves one week of events based on the given start and end date"""
    sql = '''
        SELECT *
        FROM Events
        JOIN Categories on Categories.category_id = Events.category_id
        WHERE Events.user_id = ?
        AND event_date >= ?
        AND event_date <= ?
    '''
    # NOTE: do I need to order by date ascending?

    data = (user_id, start, end)

    events = query_all(sql, data)

    return events



def get_category_id(user_id, category_str):
    """Finds the category id of a given category name string"""
    sql = '''
        SELECT category_id
        FROM Categories
        WHERE category_name = ? AND user_id = ?
    '''

    data = (category_str, user_id)

    category_id = query_one(sql, data)

    # Return the value of category_id (integer)
    return category_id['category_id']



def get_all_categories(user_id):
    """Retrieve all the user's categories"""
    sql = '''
        SELECT *
        FROM Categories 
        WHERE user_id = ?
    '''

    data = (user_id,)
    categories = query_all(sql, data)

    return categories


def check_if_add_new_category(category_str, user_id):
    """Checks whether a user has entered a new category (case sensitive). Returns a boolean."""
    categories = get_all_categories(user_id)

    for category in categories:
        if category_str in category['category_name']:
            return False
    
    return True


def select_week_dates(selected_date):
    """Returns the start date and end date of the week based on selected date object"""
    # Convert the date into an isocalendar date
    selected_date = selected_date.isocalendar()

    year = selected_date[0]
    week_num = selected_date[1]
    
    # Start date and end date of the week based on selected date
    start_date = date.fromisocalendar(year, week_num, 1)
    end_date = date.fromisocalendar(year, week_num, 7)

    # Return the date objects
    return start_date, end_date

