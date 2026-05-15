from flask import render_template, request, session, abort, redirect, url_for

from application import app
from utils.validators import validate_event, validate_date, validate_category
from utils.events import select_week_dates, check_if_add_new_category, get_all_categories, get_category_id, get_this_week_events, get_event_styling, get_this_weeks_days, get_category_details
from utils.db import get_db
from utils.user_profile import get_user_profile

def check_login():
    """Checks if a user id is set in the session"""
    if 'user_id' not in session:
        abort(401)


@app.get('/dashboard')
def dashboard():
    check_login()
    events = [
        {'time': 'idk what format', 'event_details': 'Going to school'},
        {'time': 'still dunno', 'event_details': 'Going HOME'}
    ]

    num_events = 2

    quick_note = 'Finish dashboard design and start coding new event form Finish dashboard design and start coding new event form Finish dashboard design and start coding new event form Finish dashboard design andign and start coding new event form Finish dashboard design and start coding new event form Finish dashboard design and start coding new event form Finish dashboard design and start coding new event form Finish dashboard design and start coding new event form Finish dashboard design and start coding new event form Finish dashboard design and start coding new event form '

    return render_template('app/dashboard.html', events=events, count=num_events, quick_note=quick_note)


@app.get('/edit-quick-note')
def quick_note_form():
    check_login()
    return render_template('app/quick-note.html')


@app.get('/view-timetable')
def timetable():
    check_login()

    # Validate the selected date and convert into a date object
    date_selected = validate_date(request.args.get('date_selected'))

    # Figure out what the first and last day of the week the selected date is in
    start_date, end_date = select_week_dates(date_selected)
    
    # Get the user's events for the selected week
    events = get_this_week_events(session.get('user_id'), start_date, end_date)

    # Get styling information for the events
    events_style_ls = get_event_styling(events)

    # Get every day of the selected week to display
    week_dates = get_this_weeks_days(start_date)
    
    return render_template('app/timetable.html', date_selected=date_selected, start_date=start_date, end_date=end_date, 
                           events=events, event_styles=events_style_ls, week_dates=week_dates)


@app.get('/add-event')
def new_event_form():
    check_login()
    categories = get_all_categories(session.get('user_id'))
    return render_template('app/event-form.html', categories=categories)


@app.post('/submit-new-event')
def add_event():
    check_login()
    
    # Dictionary for form data - used to repopulate the form
    form_data = {
        'event_date': request.form.get('event_date'),
        'start_time': request.form.get('start_time'),
        'is_all_day_event': 'is_all_day_event' in request.form,
        'end_time': request.form.get('end_time'),
        'event_title': request.form.get('event_title', '').strip(),
        'event_description': request.form.get('event_description', '').strip(),
        'category': request.form.get('category', '').strip()
    }

    # Validate the event submission for any errors
    errors = validate_event(form_data)

    if errors:
        # Re-render the template with error messages and form data
        return render_template('app/event-form.html', errors=errors, data=form_data, categories=get_all_categories(session.get('user_id')))

    # Get the user id from the session
    user_id = session.get('user_id')

    # Get the user entered category name
    category_name = form_data['category']
   
    # Prepare database connection
    conn = get_db()
    cursor = conn.cursor()

    if check_if_add_new_category(category_name, user_id):
        # Add the category string into the database
        sql = '''
            INSERT INTO Categories
                (user_id,
                category_name)
            VALUES (?, ?)
        '''

        data = (
            session.get('user_id'),
            category_name
        )

        cursor.execute(sql, data)
        
        # Get the category id of the newly added category
        category_id = cursor.lastrowid
    else:
        # Get the category id
        category_id = get_category_id(user_id, category_name)
        

    # Insert the trip data into the database
    sql = '''
        INSERT INTO Events
            (user_id,
            event_date,
            start_time,
            end_time,
            is_all_day_event,
            event_title,
            event_description,
            category_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    '''
    data = (
        user_id,
        form_data['event_date'],
        form_data['start_time'],
        form_data['end_time'],
        form_data['is_all_day_event'],
        form_data['event_title'],
        form_data['event_description'],
        category_id
    )

    cursor.execute(sql, data)

    # Commit changes and close the database connection
    conn.commit()
    conn.close()

    return redirect(url_for('dashboard'))



@app.get('/categories')
def view_categories():
    check_login()

    # Get a list of all the category names
    categories = get_all_categories(session.get('user_id'))
    
    return render_template('app/categories.html', categories=categories)


@app.get('/edit-category/<int:category_id>')
def edit_category(category_id):
    check_login()

    # Check the category exists and belongs to the user
    category = get_category_details(category_id, session.get('user_id'))
    if not category:
        abort(404)

    return render_template('app/categories-edit.html', data=category)

@app.post('/update-category')
def update_category():
    check_login()

    form_data = {
        'category_name': request.form.get('category_name').strip(),
        'category_id': request.form.get('category_id')
    }

    # Validate the category name
    errors = validate_category(form_data['category_name'])

    if errors:
        # Re-render the form with error messages
        return render_template('app/categories-edit.html', errors=errors, data=form_data)

    # Check that the category id was provided in the form
    try:
        category_id = int(form_data['category_id'])
    except (ValueError, TypeError):
        abort(400)

    # Get the user id
    user_id = session.get('user_id')

    # Check that the category belongs to the user
    category = get_category_details(category_id, user_id)
    if not category:
        abort(404)
    
    # Prepare database connection
    conn = get_db()
    cursor = conn.cursor()

    # TODO: TODO TODO AHHHH!!!
    sql = '''
        UPDATE Categories
        SET category_name = ?
        WHERE category_id = ?
    '''

    data = (
        form_data['category_name'],
        category_id
    )

    cursor.execute(sql, data)

    # Commit changes and close database connection
    conn.commit()
    conn.close()

    return redirect(url_for('view_categories'))
    


@app.get('/profile')
def view_profile():
    check_login()

    # Get profile details
    email_str = get_user_profile(session.get('user_id'))

    return render_template('app/profile.html', email=email_str)


@app.get('/confirm-logout')
def confirm_logout():
    check_login()
    return render_template('app/confirm-logout.html')

