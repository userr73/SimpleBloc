from datetime import date, time

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

