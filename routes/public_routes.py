from flask import render_template, redirect, url_for, request, flash, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

from application import app
from utils.validators import validate_registration, validate_login
from utils.db import get_db, query_all, query_one


@app.before_request
def check_csrf():
    # Generate a CSRF token for visitors
    if not session.get('csrf_token'):
        session['csrf_token'] = secrets.token_hex(16)

    # Perform a CSRF check for POST requests
    if request.method == "POST":
        form_token = request.form.get('csrf_token')
        session_token = session.get('csrf_token')

        # Abort the request if the tokens do not match
        if not form_token or form_token != session_token:
            abort(403, "CSRF Error")


@app.get('/')
def home():
    return render_template('public/home.html')


@app.get('/login')
def login_form():
    return render_template('public/login.html')


@app.post('/login')
def process_login_form():
    form_data = {
        'email': request.form.get('email', '').strip(),
        'password': request.form.get('password', '').strip()
    }

    # Check the form for errors
    errors = validate_login(form_data)

    if errors:
        # Re-render the form with error messages
        message = f"Login failed. Please check the form and try again or register a new account."
        flash(message, 'error-message')
        return render_template('public/login.html', 
                               data=form_data, 
                               errors=errors)
    
    # Retrieve the user details from the database
    sql = 'SELECT * FROM Users WHERE email = ?'
    data = (form_data['email'],)
    user = query_one(sql, data)

    # Determine if the login is valid
    if user:
        # Check that the entered password is correct
        valid_login = check_password_hash(user['password_hash'], form_data['password'] )
    else:
        # Invalid login - no user found with the entered email
        valid_login = False

    # Redirect to dashboard for valid login or  
    if valid_login:
        # Set the session variable and redirect to the dashboard
        session['user_id'] = user['user_id']
        
        # Generate a new CSRF token for the logged-in user
        session['csrf_token'] = secrets.token_hex(16)

        flash('Login successful!', 'info-message')
        return redirect(url_for('dashboard'))
    else:
        # Generic error message for both cases of user not found and incorrect password
        flash("Incorrect email or password", "error-message")

        # Clear the password field and re-render the form with an error message
        form_data['password'] = ''
        return render_template('public/login.html', 
                               data=form_data)


@app.get('/register')
def register_form():
    return render_template('public/register.html')


@app.post('/register')
def process_register_form():
    form_data = {
        'email': request.form.get('email', '').strip(),
        'password': request.form.get('password', '').strip(),
        'confirm_password': request.form.get('confirm_password', '').strip()
    }

    # Check for errors in the registration form
    errors = validate_registration(form_data)

    if errors:
        # Flash an error message
        flash('Registration form could not be completed. Please check the form and try again.', 'error-message')

        # Re-render the form with error messages
        return render_template('public/register.html', data=form_data, errors=errors)

    # Check that the email does not already have an account
    sql = 'SELECT email FROM Users WHERE email = ?'
    data = (form_data['email'],)

    existing_user = query_one(sql, data)

    if existing_user:
        flash('An account with this email address already exists. <a href="{url_for("login_form")}">Log in?</a>', 'error-message')
        return render_template('public/register.html', data=form_data)

     # Prepare database connection for adding a new user
    conn = get_db()
    cursor = conn.cursor()
    
    # Add our new user
    sql = '''
        INSERT INTO Users
            (email,
            password_hash,
            quick_note)
        VALUES (?, ?, ?)
    '''
    
    data = (
        form_data['email'],
        generate_password_hash(form_data['password']),
        ''
    )
    
    cursor.execute(sql, data)

    # Add the default category for the user
    sql = '''
        INSERT INTO Categories
            (user_id,
            category_name,
            category_colour)
        VALUES (?, ?, ?)
    '''

    data = (
        cursor.lastrowid,
        'No category',
        '#D3D3D3'
    )

    cursor.execute(sql, data)

    conn.commit()
    conn.close()

    flash('Registration successful! Login below.', 'info-message')
    return redirect(url_for('login_form'))


@app.post('/logout-successful')
def logout():
    session.clear()
    return render_template('public/logout.html')

