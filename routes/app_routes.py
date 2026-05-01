from flask import render_template, request, session, abort, redirect, url_for

from application import app
from utils.validators import validate_event, validate_date
from utils.events import select_week_dates, check_if_add_new_category, get_all_categories, get_category_id
from utils.db import get_db

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

    # events = []

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
    events = [
        {'time': 'idk what format', 'event_details': 'Going to school'},
        {'time': 'still dunno', 'event_details': 'Going HOME'}
    ]

    # Validate the selected date and convert into a date object
    print(request.form.get('date_selected'))
    date_selected = validate_date(request.form.get('date_selected'))

    start_date, end_date = select_week_dates(date_selected)

    return render_template('app/timetable.html', date_selected=date_selected.isoformat(), start_date=start_date, end_date=end_date)


@app.get('/add-event')
def new_event_form():
    check_login()
    categories_list = get_all_categories(session.get('user_id'))
    return render_template('app/event-form.html', categories=categories_list)


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
    
    if check_if_add_new_category(category_name, user_id):
        # Add the category string into the database
        conn = get_db()
        cursor = conn.cursor()

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

        conn.commit()
        conn.close()
    
    # Get the category id of the user inputted category name
    category_id = get_category_id(user_id, category_name)

    # Prepare database connection
    conn = get_db()
    cursor = conn.cursor()

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



@app.get('/edit-categories')
def edit_categories():
    check_login()
    categories = ['school', 'sport', 'sleep']
    
    return render_template('app/categories.html', categories=categories)


@app.get('/profile')
def view_profile():
    check_login()
    return render_template('app/profile.html')


@app.get('/confirm-logout')
def confirm_logout():
    check_login()
    return render_template('app/confirm-logout.html')

