from flask import render_template, request, session, abort, redirect, url_for
from werkzeug.security import generate_password_hash

from application import app
from utils.validators import validate_event, validate_date, validate_category, validate_email, validate_password_change_form
from utils.events import select_week_dates, check_if_add_new_category, get_all_categories, get_all_user_custom_categories, get_category_id, get_this_week_events, get_event_styling, get_this_weeks_days, get_category_details, get_event_details, is_default_category, date_to_local_format, date_to_day_name
from utils.db import get_db
from utils.user_profile import get_user_profile, get_default_category_id, get_quick_note

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

    # Retrieve the user's quick note from the database
    quick_note = get_quick_note(session.get('user_id'))

    return render_template('app/dashboard.html', 
                           events=events, 
                           count=num_events, 
                           quick_note=quick_note)


@app.get('/edit-quick-note')
def quick_note_form():
    check_login()

    # Retrieve the user's quick note from the database
    quick_note = get_quick_note(session.get('user_id'))
    print("USERS QUICK NOTE", quick_note)

    return render_template('app/quick-note.html',
                           quick_note=quick_note)


@app.post('/edit-quick-note')
def update_quick_note():
    check_login()

    # Retrieve the quick note value
    quick_note = request.form.get('quick_note').strip()

    # Get the user id from session
    user_id = session.get('user_id')

    # Prepare database connection
    conn = get_db()
    cursor = conn.cursor()

    sql = '''
        UPDATE Users
        SET quick_note = ?
        WHERE user_id = ?
    '''

    data = (
        quick_note,
        user_id
    )

    cursor.execute(sql, data)

    # Commit changes and close database connection
    conn.commit()
    conn.close()

    return redirect(url_for('dashboard'))


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
    
    return render_template('app/timetable.html', 
                           date_selected=date_selected, 
                           start_date=start_date, 
                           end_date=end_date, 
                           events=events, 
                           event_styles=events_style_ls, 
                           week_dates=week_dates)


@app.get('/event/<int:event_id>')
def view_event(event_id):
    check_login()

    # Get event dictionary
    event = get_event_details(event_id, session.get('user_id'))

    # Check that the event belongs to the user
    if not event:
        abort(404)
    
    # Get the event date
    event_date_str = event['event_date']

    # Find the day of the week of the event date
    event_day_of_week = date_to_day_name(event_date_str)
    event['day_of_week'] = event_day_of_week

    # Convert event date to local formatting
    event_date_formatted = date_to_local_format(event_date_str)
    event['event_date'] = event_date_formatted

    return render_template('app/event.html', event=event)


@app.get('/add-event')
def new_event_form():
    check_login()
    categories = get_all_categories(session.get('user_id'))
    
    data = {}
    # Set the category name to always be the default
    data['category_name'] = 'No category'

    return render_template('app/event-form.html', 
                           mode='add', 
                           categories=categories, 
                           data=data)


@app.get('/edit-event/<int:event_id>')
def edit_event(event_id):
    check_login()

    # Check that the event belongs to the user
    event = get_event_details(event_id, session.get('user_id'))
    if not event:
        abort(404)

    # Get all user categories
    categories = get_all_categories(session.get('user_id'))

    return render_template('app/event-form.html', 
                           mode='edit', 
                           data=event, 
                           categories=categories)


@app.post('/submit-new-event')
def add_or_edit_event():
    check_login()

    # Check existence and validity of mode
    mode = request.form.get('mode')
    if mode not in ['add', 'edit']:
        abort(400)
    
    # Dictionary for form data - used to repopulate the form
    form_data = {
        'event_id': request.form.get('event_id'), # Unused for adding a new event
        'event_date': request.form.get('event_date'),
        'start_time': request.form.get('start_time'),
        'is_all_day_event': 'is_all_day_event' in request.form,
        'end_time': request.form.get('end_time'),
        'event_title': request.form.get('event_title', '').strip(),
        'event_description': request.form.get('event_description', '').strip(),
        'category_name': request.form.get('category_name', '').strip()
    }

    # Get the user id from the session
    user_id = session.get('user_id')

    # Validate the event submission for any errors
    errors = validate_event(form_data, user_id)

    if errors:
        # Re-render the template with error messages and form data
        return render_template('app/event-form.html', 
                               mode=mode,
                               errors=errors, 
                               data=form_data, 
                               categories=get_all_categories(session.get('user_id')))

    # Get the user entered category name
    category_name = form_data['category_name']
   
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
        
    
    if mode == 'add':
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
    
    else:
        # Check that a valid event ID was provided in the form
        try:
            event_id = int(request.form.get('event_id'))
        except (ValueError, TypeError):
            abort(400)
        
        # Check that the event belongs to the user
        event = get_event_details(event_id, user_id)
        if not event:
            abort(404)

        # Save changes to the database
        sql = '''
            UPDATE Events
            SET event_date = ?,
                start_time = ?,
                end_time = ?,
                is_all_day_event = ?,
                event_title = ?,
                event_description = ?,
                category_id = ?
            WHERE event_id = ?
        '''

        data = (
            form_data['event_date'],
            form_data['start_time'],
            form_data['end_time'],
            form_data['is_all_day_event'],
            form_data['event_title'],
            form_data['event_description'],
            category_id,
            event_id
        )

        cursor.execute(sql, data)

    # Commit changes and close the database connection
    conn.commit()
    conn.close()

    return redirect(url_for('dashboard'))


@app.get('/delete-event/<int:event_id>')
def confirm_delete_event(event_id):
    """Displays the confirmation page for deleting an event"""
    check_login()

    # Check that event belongs to user
    event = get_event_details(event_id, session.get('user_id'))
    if not event:
        abort(404)
    
    # Get the event date
    event_date_str = event['event_date']
    
    # Convert event date to local formatting
    event_date_formatted = date_to_local_format(event_date_str)
    event['event_date'] = event_date_formatted

    return render_template('app/event-delete.html', event=event)


@app.post('/delete-event')
def delete_event():
    """Handles the deletion of an event"""
    check_login()

    # Check that a valid event_id was provide in the form
    try:
        event_id = int(request.form.get('event_id'))
    except (ValueError, TypeError):
        abort(400)
    
    # Get the user id from session
    user_id = session.get('user_id')

    # Check event belongs to the user
    event = get_event_details(event_id, user_id)
    if not event:
        abort(404)
    
    # Prepare database connection
    conn = get_db()
    cursor = conn.cursor()

    # Delete the event from the dataabs
    sql = 'DELETE FROM Events WHERE event_id = ?'
    data = (event_id,)
    cursor.execute(sql, data)

    # Commit and close database connection
    conn.commit()
    conn.close()

    return render_template('app/dashboard.html')


@app.get('/categories')
def view_categories():
    check_login()

    # Get a list of all the category names except the default
    categories = get_all_user_custom_categories(session.get('user_id'))
    
    return render_template('app/categories.html', categories=categories)


@app.get('/edit-category/<int:category_id>')
def edit_category(category_id):
    check_login()

    # Check the category exists and belongs to the user
    category = get_category_details(category_id, session.get('user_id'))
    if not category:
        abort(404)

    # Check whether the category entered in the url is the default category (which every user must have)
    if is_default_category(category_id, 'No category'):
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


@app.get('/delete-category/<int:category_id>')
def confirm_delete_category(category_id):
    """Displays confirmation page for deleting a category"""
    check_login()

    # Check the category belongs to user
    category = get_category_details(category_id, session.get('user_id'))
    if not category:
        abort(404)

    # Check whether the category entered in the url is the default category (which every user must have)
    if is_default_category(category_id, 'No category'):
        abort(404)
    
    return render_template('app/categories-delete.html', data=category)


@app.post('/delete-category')
def delete_category():
    """Handles the deletion of a category"""
    check_login()

    # Check that a valid category_id was provided in the form
    try:
        category_id = int(request.form.get('category_id'))
    except (ValueError, TypeError):
        abort(400)
    
    user_id = session.get('user_id')

    # Check category belongs to user
    category = get_category_details(category_id, user_id)

    if not category:
        abort(404)
    
    # Prepare database connection
    conn = get_db()
    cursor = conn.cursor()

    # Change all events with that category_id to the default category's id
    sql = '''
        UPDATE Events
        SET category_id = ?
        WHERE category_id = ?
    '''

    data = (
        get_default_category_id(user_id),
        category_id
    )

    cursor.execute(sql, data)

    # Delete the category from the database
    sql = 'DELETE FROM Categories WHERE category_id = ?'
    data = (category_id,)
    cursor.execute(sql, data)

    conn.commit()
    conn.close()

    return render_template('app/categories.html')


@app.get('/profile')
def view_profile():
    check_login()

    # Get the user's profile information
    profile = get_user_profile(session.get('user_id'))

    return render_template('app/profile.html', email=profile['email'])


@app.get('/update-email')
def email_form():
    check_login()

    # Get the user's profile information
    profile = get_user_profile(session.get('user_id'))

    # Get user's email
    email = profile['email']

    return render_template('app/email.html', user_email=email)


@app.post('/submit-email')
def submit_email_change():
    check_login()
    # Get the email from the form for repopulation
    user_email = request.form.get('user_email')

    # Validate the email
    errors = validate_email(user_email)
    
    if errors:
        # Re-render the template with error messages and form data
        return render_template('app/email.html',
                               errors=errors,
                               user_email=user_email)
    
    # Get the user id from the session
    user_id = session.get('user_id')

    # Prepare database connection
    conn = get_db()
    cursor = conn.cursor()

    sql = '''
        UPDATE Users
        SET email = ?
        WHERE user_id = ?
    '''

    data = (
        user_email,
        user_id
    )

    cursor.execute(sql, data)

    # Commit changes and close the database connection
    conn.commit()
    conn.close()

    return redirect(url_for('view_profile'))



@app.get('/change-password')
def password_form():
    check_login()

    return render_template('app/password.html')


@app.post('/submit-password')
def submit_password_change():
    check_login()

    form_data = {
        'current_pwd': request.form.get('current_pwd', '').strip(),
        'new_pwd': request.form.get('new_pwd', '').strip(),
        'confirm_new_pwd': request.form.get('confirm_new_pwd', '').strip()
    }

    # Get the user id
    user_id = session.get('user_id')

    # Check the form for errors
    errors = validate_password_change_form(form_data, user_id)

    if errors:
        # Re-render the form with error messages
        return render_template('app/password.html',
                               data=form_data,
                               errors=errors)

    # Prepare the database connection
    conn = get_db()
    cursor = conn.cursor()

    sql = '''
        UPDATE Users
        SET password_hash = ?
        WHERE user_id = ?
    '''

    data = (
        generate_password_hash(form_data['new_pwd']),
        user_id
    )

    cursor.execute(sql, data)

    # Commit changes and close database connection
    conn.commit()
    conn.close()

    return redirect(url_for('view_profile'))


@app.get('/confirm-logout')
def confirm_logout():
    check_login()
    return render_template('app/confirm-logout.html')

