"""
1. Creates the application object (app)
2. Sets application configuration
3. Imports routes and utility functions
"""

from flask import Flask
import os

# Create the app
app = Flask(__name__)

app.config['DATABASE_NAME'] = 'simplebloc.db'
app.config['SECRET_KEY'] = 'temp secret' # TEMP CHANGE DELETE
# app.config['SECRET_KEY'] = os.urandom(24) 

# Route functions must be imported after the app object is created
from routes import public_routes
from routes import app_routes
from routes import error_routes
