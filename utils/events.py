from datetime import date, timedelta, time
from random import choice

from utils.db import get_db, query_all, query_one

def random_colour():
    """Retrieves a random colour"""
    colours = [
        "#FF8989",
        "#FFBB3C",
        "#FFED95",
        "#8ECE8E",
        "#7ABCFE",
        "#CD96FD",
        "#FFC0D6",
        "#B79090",
    ]

    return choice(colours)

def date_forward_one_week(date_input):
    """Returns the date a week in the future"""
    # Remove 7 days
    next_week_date = date_input + timedelta(days=7)

    return next_week_date

def date_back_one_week(date_input):
    """Returns the date a week prior"""
    # Remove 7 days
    previous_week_date = date_input - timedelta(days=7)

    return previous_week_date

def get_todays_events(user_id):
    """Retrieve the user's events for the day."""
    # Get the all day events first
    sql = '''
        SELECT start_time, end_time, is_all_day_event, event_title
        FROM Events
        WHERE event_date = ? 
        AND user_id = ?
        AND is_all_day_event = ?
    '''

    data = (
        date.today(),
        user_id,
        1
    )

    events = query_all(sql, data)

    # Get the remaining events
    sql = '''
        SELECT start_time, end_time, is_all_day_event, event_title
        FROM Events
        WHERE event_date = ? 
        AND user_id = ?
        AND is_all_day_event = ?
    '''

    data = (
        date.today(),
        user_id,
        0
    )

    events.extend(query_all(sql, data))

    return events

def get_overlapping_events(user_id, event_id, input_date, start_time, end_time):
    """Retrieves the user's overlapping events on a given day, filtered with the start and end time to determine any overlapping events."""
    # Check whether to exclude the current event from query
    if event_id:
        sql = '''
            SELECT start_time, end_time, event_title
            FROM Events
            WHERE event_date = ? 
            AND user_id = ?
            AND is_all_day_event = ?
            AND event_id != ?
        '''
        data = (
            input_date, 
            user_id,
            0,
            event_id
        )
    else:
        sql = '''
            SELECT start_time, end_time, event_title
            FROM Events
            WHERE event_date = ? 
            AND user_id = ?
            AND is_all_day_event = ?
        '''
        data = (
            input_date, 
            user_id,
            0
        )
    
    events = query_all(sql, data)

    # Create empty list for name of overlapping events
    overlaps = []

    for event in events:
        existing_start_time = start_time
        existing_end_time = end_time

        event_start = time.fromisoformat(event['start_time'])
        event_end = time.fromisoformat(event['end_time'])

        if existing_start_time < event_start and existing_end_time > event_start:
            overlaps.append(event['event_title'])
        elif existing_start_time >= event_start and existing_start_time < event_end:
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
        SELECT category_name, category_id, category_colour
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


def get_all_day_event_styling(events_dict):
    """Returns a dictionary of lists of colours for the all day events"""
    event_styles = {}

    for day_num, events in events_dict.items():
        if events:
            # First create a new key value pair in the dictionary based on the day number
            event_styles[day_num] = [events[0]['category_colour']]
            
            # Add the remaining events (if any) to the list
            for event in events[1:]:
                event_styles[day_num].append(event['category_colour'])

    return event_styles


def get_normal_event_styling(events):
    """Returns a list of dictionaries containing the column name, row start and end values and the category colour"""
    events_style_ls = []

    for event in events:
        # Get the column name
        col_name = date_to_day_name(event['event_date'])

        # Get the row start and end numbers
        row_start = time_to_row_num(event['start_time'])
        row_end = time_to_row_num(event['end_time'])

        # Get the category colour
        colour = event['category_colour']

        # Add these column and row values to a dictionary
        event_dict = {
            'col_name': col_name, 
            'row_start': row_start, 
            'row_end': row_end,
            'colour': colour
        }
        
        # Add the dictionary as a list item
        events_style_ls.append(event_dict)
    
    return events_style_ls


def get_this_weeks_events(user_id, start, end):
    """Retrieves one week of events based on the given start and end date"""
    week_events = {}

    # Get the normal events
    sql = '''
        SELECT *
        FROM Events
        JOIN Categories on Categories.category_id = Events.category_id
        WHERE Events.user_id = ?
        AND event_date >= ?
        AND event_date <= ?
        AND is_all_day_event = ?
    '''

    data = (
        user_id, 
        start, 
        end,
        0
    )

    normal_events = query_all(sql, data)

    week_events['normal'] = normal_events

    # Get the all day events
    sql = '''
        SELECT *
        FROM Events
        JOIN Categories on Categories.category_id = Events.category_id
        WHERE Events.user_id = ?
        AND event_date >= ?
        AND event_date <= ?
        AND is_all_day_event = ?
        ORDER BY event_date ASC
    '''

    data = (
        user_id, 
        start, 
        end,
        1
    )

    all_day_events = query_all(sql, data)

    if all_day_events:
        sorted_ad_events = {}
        # Get the number of all day events
        num_events = len(all_day_events)

        # Set current date to the start date provided
        current_date = start
        
        # Set the initial day number to 1
        day_num = 1

        for event in all_day_events:
            # Get the event date date object
            event_date_obj = date.fromisoformat(event['event_date'])

            if event_date_obj == current_date:
                sorted_ad_events[day_num].append(event)
            else:
                # Check if the day number is a key in the dictionary
                if day_num not in sorted_ad_events:
                    sorted_ad_events[day_num] = None
                
                # Get the difference in the previous day and new day
                difference = num_days_difference(current_date, event_date_obj)
                new_day_num = day_num + difference

                # For day numbers between current day and new day (non-inclusive)
                # they should be assigned None as well
                for i in range(day_num+1, new_day_num):
                    sorted_ad_events[i] = None
                
                day_num = new_day_num
                current_date = event_date_obj

                # Add the new key value pair 
                sorted_ad_events[day_num] = [event]
        
        # Set value as None for remaining day numbers if there are no all day events
        while day_num < 7:
            day_num += 1
            sorted_ad_events[day_num] = None
    
        week_events['all_day'] = sorted_ad_events
    else:
        no_all_day_dict = {}
        for i in range(1, 8):
            no_all_day_dict[i] = None
        
        week_events['all_day'] = no_all_day_dict

    return week_events


def num_days_difference(start, end):
    """Returns the number of days between two date objects"""
    difference = end - start

    return difference.days


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

