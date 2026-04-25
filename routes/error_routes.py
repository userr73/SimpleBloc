from flask import render_template
from application import app

@app.errorhandler(401)
def not_found_error(error):
    return render_template('error/401.html'), 401
