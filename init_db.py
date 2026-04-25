"""
WARNING: Running this file deletes any existing data if the database already exists
"""

import sqlite3
from application import app

# Name of database and location of schema file
DATABASE_NAME = app.config['DATABASE_NAME']
SCHEMA_FILENAME = 'simplebloc-schema.sql'

# Establish a connection to the database
conn = sqlite3.connect(DATABASE_NAME)

# Create the database using the schema file
with open(SCHEMA_FILENAME) as f:
    conn.executescript(f.read())

# Commit the changes and close the connection
conn.commit()
conn.close()

print(f"SUCCESS: {DATABASE_NAME} created")








