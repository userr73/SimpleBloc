from flask import Flask, render_template

from application import app

@app.get('/')
def home():
    return render_template('public/home.html')


@app.get('/login')
def login_form():
    return render_template('public/login.html')


@app.get('/register')
def register_form():
    return render_template('public/register.html')


@app.get('/logout')
def confirm_logout():
    return render_template('public/logout.html')

