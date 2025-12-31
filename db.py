import sqlite3
from contextlib import contextmanager


# ---------------- DB LAYER FUNCTIONS ----------------

def get_subjects(user_id):
    with open_db() as cur:
        cur.execute("SELECT id, name FROM subjects WHERE user_id = ?", (user_id,))
        return cur.fetchall()
    

def username_exists(username):
    with open_db() as cur:
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        if cur.fetchone():
            return True
        return False
    
    
def add_subject_db(subject_name, subject_user_id):
    with open_db() as cur:
        cur.execute("INSERT INTO subjects (user_id, name) VALUES (?, ?)", (subject_user_id, subject_name))   


def delete_subject_db(subject_id):
    with open_db() as cur:
        cur.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
        
        
def subject_exists(subject_name, subject_user_id):
    with open_db() as cur:
        cur.execute("SELECT * FROM subjects WHERE name = ? AND user_id = ?", (subject_name, subject_user_id)) 
        if cur.fetchone():
            return True
    return False   
    
    
def get_chapters(subject_id):
    with open_db() as cur:
        cur.execute("SELECT * FROM chapters WHERE subject_id = ?", (subject_id,))
        return cur.fetchall()


def get_topics(subject_id):
    with open_db() as cur:
        cur.execute("SELECT t.*, COUNT(s.id) AS session_count, SUM(s.duration) AS total_duration, MIN(s.date) AS first_session_date FROM topics t LEFT JOIN sessions s ON t.id = s.topic_id WHERE t.subject_id = ? GROUP BY t.id;", (subject_id,))
        return cur.fetchall()
    
        
def get_subject_details(subject_id):
    with open_db() as cur:
        cur.execute("""SELECT sub.*,
                    (SELECT COUNT(*) FROM topics WHERE subject_id = sub.id) AS topic_count,
                    (SELECT COUNT(*) FROM sessions WHERE subject_id = sub.id) AS session_count,
                    (SELECT SUM(sessions.duration) FROM sessions WHERE subject_id = sub.id) AS total_duration,
                    (SELECT MAX(sessions.date) FROM sessions WHERE subject_id = sub.id) AS last_session_date
                    FROM subjects sub WHERE sub.id = ?""", (subject_id,))       
        return cur.fetchone()                 
    
    
def get_dashboard_summary(day_start, day_end, user_id):
    with open_db() as cur:
        cur.execute("""SELECT 
                    SUM(duration) AS total_duration,
                    COUNT(*) AS total_sessions 
                    FROM sessions WHERE date >= ? AND date < ? AND subject_id IN 
                    (SELECT id FROM subjects WHERE user_id = ?);
                    """, (day_start, day_end, user_id))
        return cur.fetchone()
    
    
def get_dashboard_details(day_start, day_end, user_id):
    with open_db() as cur:
        cur.execute("""SELECT 
                        sub.name, 
                        GROUP_CONCAT(DISTINCT t.name) AS subject_topics,
                        SUM(ses.duration) AS total_duration,
                        COUNT(ses.id) AS total_session_count,
                        COUNT(CASE WHEN ses.topic_id IS NULL THEN 1 END) AS topicless_session_count
                        FROM subjects sub 
                        JOIN sessions ses ON ses.subject_id = sub.id 
                        LEFT JOIN topics t ON ses.topic_id = t.id
                        WHERE ses.date >= ? AND ses.date < ? AND sub.user_id = ?
                        GROUP BY sub.id;
                    """, (day_start, day_end, user_id))
        return cur.fetchall()
    
    
def add_user(username, password_hash):
    with open_db() as cur:
        cur.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))


def get_subject_name(subject_id):
    with open_db() as cur:
        cur.execute("SELECT name FROM subjects WHERE id = ?", (subject_id,))


def topic_exists(topic_name, subject_id):
    with open_db() as cur:
        cur.execute("SELECT * FROM topics WHERE subject_id = ? AND name = ?", (subject_id, topic_name))
        if cur.fetchone():
            return True
    return False


def chapter_exists(chapter_name, subject_id):
    with open_db() as cur:
        cur.execute("SELECT * FROM chapters WHERE subject_id = ? AND name = ?", (subject_id, chapter_name))
        
        
def add_topic_db(topic_name, subject_id):
    with open_db() as cur:
        cur.execute("INSERT INTO topics (subject_id, name) VALUES (?, ?)", (subject_id, topic_name))


def delete_topic_db(topic_id):
    with open_db() as cur:
        cur.execute("DELETE FROM topics WHERE id = ?", (topic_id,))
def add_chapter_db(chapter_name, subject_id):
    with open_db() as cur:
        cur.execute("INSERT INTO chapters (subject_id, name) VALUES (?, ?)", (subject_id, chapter_name))
        

def delete_chapter_db(chapter_id):
    with open_db() as cur:
        cur.execute("DELETE FROM chapters WHERE id = ?", (chapter_id,))
        
        
def assign_topic_chapter(topic_id, chapter_id):
    with open_db() as cur:
        cur.execute("UPDATE topics SET chapter_id = ? WHERE id = ?", (chapter_id, topic_id))
        

def add_session(subject_id, duration):
    with open_db() as cur:
        cur.execute("INSERT INTO sessions (subject_id, duration) VALUES (?, ?)", (subject_id, duration))
        return cur.lastrowid
    
    
def add_session_topic(session_id, topic_id):
    with open_db() as cur:
        cur.execute("UPDATE sessions SET topic_id = ? WHERE id = ?", (topic_id, session_id))
        

    
    
# Improvement: Also checks for password_hash
def get_user_id(username):
    with open_db() as cur:
        cur.execute("SELECT id FROM users WHERE username = ?", (username,))
        return cur.fetchone()["id"]
    

def get_subject_id(subject_name, user_id):
    with open_db() as cur:
        cur.execute("SELECT id FROM subjects WHERE user_id = ? AND name = ?", (user_id, subject_name))
        return cur.fetchone()["id"]
        
        
def get_topic_id(topic_name, subject_id):
    with open_db() as cur:
        cur.execute("SELECT id FROM topics WHERE subject_id = ? AND name = ?", (subject_id, topic_name))
        return cur.fetchone()["id"]
    
    
def get_username(user_id):
    with open_db() as cur:
        cur.execute("SELECT username FROM users WHERE id = ?", (user_id,))
        return cur.fetchone()["username"]

def get_hash(username):    
    with open_db() as cur:
        cur.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
        return cur.fetchone()["password_hash"]
        

# Initializes database schema
def init_db():
    conn = sqlite3.connect("study_tracker.db")
    conn.row_factory = sqlite3.Row

    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL 
        )               
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            UNIQUE(user_id, name),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE 
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chapters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            UNIQUE(subject_id, name),
            FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
        );
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS topics (            
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL,
            chapter_id INTEGER DEFAULT NULL,
            name TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (subject_id, name),
            FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE CASCADE,
            FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
        );
    """)

    # THIS SHOULD BE CHANGED 
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL,
            topic_id INTEGER,
            duration INTEGER NOT NULL,
            date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
            FOREIGN KEY(topic_id) REFERENCES topics(id) ON DELETE CASCADE 
        );
    """)

    conn.commit()
    conn.close()


# Context manager that handles DB connection lifecycle
@contextmanager
def open_db():
    conn = sqlite3.connect("study_tracker.db")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()
    try:
        yield cur
        conn.commit()
    finally:
        conn.close()
