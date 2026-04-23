from flask import Flask, render_template, request

from utils.validators import validate_event, validate_date
from utils.events import select_week_dates

from application import app


@app.get('/dashboard')
def dashboard():
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
    return render_template('app/quick-note.html')


@app.get('/view-timetable')
def timetable():
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
    return render_template('app/event-form.html')


@app.post('/submit-new-event')
def submit_new_event():
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
        return render_template('app/event-form.html', errors=errors, data=form_data)

    # If no errors, use temp submission form
    form_data['event_date'] 
    return render_template('app/temp-form-submit.html', data=form_data)


@app.get('/edit-categories')
def edit_categories():
    categories = ['school', 'sport', 'sleep']
    
    return render_template('app/categories.html', categories=categories)


@app.get('/profile')
def view_profile():
    return render_template('app/profile.html')



