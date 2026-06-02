from datetime import date, time, timedelta, datetime
from utils.db import query_one
from werkzeug.security import check_password_hash

def validate_password_change_form(form_data, user_id):
    """Validates the password change form"""
    # Create empty errors dictionary
    errors = {}

    # Current password must be entered
    current_pwd = form_data['current_pwd']

    if not current_pwd:
        errors['current_pwd'] = 'Enter your current password'
    else:
        # Retrieve the user's password hash
        sql = 'SELECT password_hash FROM Users WHERE user_id = ?'
        data = (user_id,)
        password_hash = query_one(sql, data)['password_hash']

        # The password the user entered must match their current password
        is_correct_pwd = check_password_hash(password_hash, current_pwd)

        if not is_correct_pwd:
            errors['current_pwd'] = 'Incorrect password'
    
    # New password is mandatory and must be at least 8 characters long
    new_pwd = form_data['new_pwd']
    if len(new_pwd) < 8:
        errors['new_pwd'] = 'New password must be at least 8 characters long'

    # Password confirmation must match password
    if new_pwd != form_data['confirm_new_pwd']:
        errors['confirm_new_pwd'] = 'Passwords do not match'

    return errors


def validate_email(email):
    """Validates the email input field. Returns any error messages."""
    # Email is mandatory and must be a valid email format
    if '@' not in email or len(email) < 3:
        return 'Enter a valid email address'
    
    return None


def validate_category(category_name):
    """Validates the category input field. Returns any error messages."""
    # Category cannot be empty
    if not category_name:
        return 'Enter a category'
    
    return None


def validate_login(data):
    """Validates the login form for an existing user"""

    # Dictionary for form errors
    errors = {}

    # Email is mandatory and must be in a valid format
    if '@' not in data['email'] or len(data['email']) < 3:
        errors['email'] = 'Enter a valid email address'

    # Password is mandatory
    if not data['password']:
        errors['password'] = 'Enter your password'

    return errors


def validate_registration(data):
    """Validates the registration form"""

    # Dictionary for form errors
    errors = {}

    # Email is mandatory and must be a valid email format
    if '@' not in data['email'] or len(data['email']) < 3:
        errors['email'] = 'Enter a valid email address'

    # Password is mandatory and must be at least 8 characters long
    if len(data['password']) < 8:
        errors['password'] = 'Password must be at least 8 characters long'

    # Password confirmation must match password
    if data['password'] != data['confirm_password']:
        errors['confirm_password'] = 'Passwords do not match'
    
    return errors
    

def validate_date(date_input):
    """Validates the date input from the date selector in the timetable and returns a valid date object"""
    try:
        # Try to create a Python date object to verify it is a valid date
        valid_date = date.fromisoformat(date_input)
    except (ValueError, TypeError):
        valid_date = date.today()
    
    return valid_date


def validate_event(data):
    """Validates the event form to add or edit an event"""

    # Dictionary for form errors
    errors = {}

    # Must be a valid date
    try:
        # Try to create a Python date object to verify it is a valid date
        event_date = date.fromisoformat(data['event_date'])
    except ValueError:
        errors['event_date'] = 'Enter a valid date'
    
    # Check if the event is not an all day event so time needs validation
    if not data['is_all_day_event']:
        # Start time is mandatory
        start_time = None
        if not data['start_time']:
            errors['start_time'] = 'Enter the start time of the event'
        else:
            # Check time is a valid time
            try:
                start_time = time.fromisoformat(data['start_time'])
            except ValueError:
                errors['start_time'] = 'Enter a valid time'

        # End time is mandatory
        end_time = None
        if not data['end_time']:
            errors['end_time'] = 'Enter the end time of the event'
        else:
            # Check time is a valid time
            try:
                end_time = time.fromisoformat(data['end_time'])
            except ValueError:
                errors['end_time'] = 'Enter a valid time'


        if start_time and end_time:
            # End time must be later than start time
            if end_time <= start_time:
                errors['end_time'] = 'The end time must be later than the start time'
            else:
                # Check that the event is at least 10 min long
                # Convert start time to a datetime object with a dummy date
                start_time_date_obj = datetime.combine(date.today(), start_time)

                # Add ten minutes to get the minimum end time
                min_end_time_date_obj = start_time_date_obj + timedelta(minutes=10)
                min_end_time = min_end_time_date_obj.time()
                
                # Event must be at least 10 min long
                if end_time < min_end_time:
                    errors['end_time'] = 'Event must be at least 10 minutes long'


    # Event title is mandatory
    if not data['event_title']:
        errors['event_title'] = 'Enter the event title'
    
    # Event description is mandatory
    if not data['event_description']:
        errors['event_description'] = 'Enter the event description'

    # Category cannot be empty
    if not data['category_name']:
        errors['category_name'] = 'Enter a category'

    return errors

