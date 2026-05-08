from datetime import date

from utils.db import get_db, query_all, query_one

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
        SELECT category_name 
        FROM Categories 
        WHERE user_id = ?
    '''

    data = (user_id,) 
    categories_row_obj = query_all(sql, data)

    # Retrieve the category name from each row of the category object
    categories_list = [category['category_name'] for category in categories_row_obj]

    return categories_list


def check_if_add_new_category(category_str, user_id):
    """Checks whether a user has entered a new category (case sensitive). Returns a boolean."""
    categories_list = get_all_categories(user_id)

    if category_str not in categories_list:
        return True

    return False


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

    # Return the date objects
    return start_date, end_date

