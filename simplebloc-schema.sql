-- Delete all tables if they exist
DROP TABLE IF EXISTS Users;
DROP TABLE IF EXISTS Categories;
DROP TABLE IF EXISTS Events;

-- User details
CREATE TABLE Users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    quick_note TEXT NOT NULL
);

-- Details of all categories created by users
CREATE TABLE Categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category_name TEXT NOT NULL,
    category_colour TEXT NOT NULL,
    
    FOREIGN KEY (user_id) REFERENCES Users (user_id)
);

-- All events created by users
CREATE TABLE Events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    event_date TEXT NOT NULL,
    start_time TEXT,
    end_time TEXT,
    is_all_day_event INTEGER,

    event_title TEXT NOT NULL,
    event_description TEXT NOT NULL,
    category_id INTEGER NOT NULL,

    FOREIGN KEY (user_id) REFERENCES Users (user_id),
    FOREIGN KEY (category_id) REFERENCES Categories (category_id)
);

