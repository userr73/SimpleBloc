from flask import Flask, render_template

app = Flask(__name__)

@app.get('/')
def home():
    return render_template('public/home.html')


@app.get('/login')
def login_form():
    return render_template('public/login.html')


@app.get('/register')
def register_form():
    return render_template('public/register.html')

@app.get('/dashboard')
def dashboard():
    # events = [
    #     {'time': 'idk what format', 'event_details': 'Going to school'},
    #     {'time': 'still dunno', 'event_details': 'Going HOME'}
    # ]

    events = []

    num_events = 2

    quick_note = 'Finish dashboard design and start coding new event form Finish dashboard design and start coding new event form Finish dashboard design and start coding new event form Finish dashboard design andign and start coding new event form Finish dashboard design and start coding new event form Finish dashboard design and start coding new event form Finish dashboard design and start coding new event form Finish dashboard design and start coding new event form Finish dashboard design and start coding new event form Finish dashboard design and start coding new event form '

    return render_template('app/dashboard.html', events=events, count=num_events, quick_note=quick_note)

@app.get('/edit-quick-note')
def quick_note_form():
    return render_template('app/quick-note.html')

@app.get('/view-timetable')
def timetable():
    return render_template('app/timetable.html')

@app.get('/add-event')
def new_event_form():
    return render_template('app/event-form.html')

@app.get('/profile')
def view_profile():
    return render_template('app/profile.html')

@app.get('/logout')
def confirm_logout():
    return render_template('public/logout.html')

app.run(debug=True)
