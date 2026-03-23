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
    return render_template('app/dashboard.html')

@app.get('/view-timetable')
def timetable():
    return render_template('app/timetable.html')

@app.get('/add-event')
def add_event_form():
    return render_template('app/event-form.html')

@app.get('/profile')
def view_profile():
    return render_template('app/profile.html')

@app.get('/logout')
def confirm_logout():
    return render_template('public/logout.html')

app.run(debug=True)
