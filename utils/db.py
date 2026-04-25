import sqlite3
from application import app

def get_db():
    """Returns a database connection object"""
    db = sqlite3.connect(app.config['DATABASE_NAME'])
    db.row_factory = sqlite3.Row
    return db

def query_one(sql, data=()):
    """Returns a single result (row)"""
    conn = get_db()
    cursor = conn.cursor()
    result = cursor.execute(sql, data).fetchone()
    conn.close()
    return result

def query_all(sql, data=()):
    """Returns a list of results"""
    conn = get_db()
    cursor = conn.cursor()
    results = cursor.execute(sql, data).fetchall()
    conn.close()
    return results
