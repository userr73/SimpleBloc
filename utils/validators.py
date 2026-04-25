from datetime import date, time

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

        # End time must be later than start time
        if start_time and end_time:
            if end_time <= start_time:
                errors['end_time'] = 'The end time must be later than the start time'

    # Event title is mandatory
    if not data['event_title']:
        errors['event_title'] = 'Enter the event title'
    
    # Event description is mandatory
    if not data['event_description']:
        errors['event_description'] = 'Enter the event description'

    # Category cannot be empty
    if not data['category']:
        errors['category'] = 'Enter a category'

    return errors

