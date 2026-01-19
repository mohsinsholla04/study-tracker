import sqlite3
from contextlib import contextmanager


# ---------------- DB LAYER FUNCTIONS ----------------

# ****** Users ******* 
def username_exists(username):
    with open_db() as cur:
        cur.execute("SELECT 1 FROM users WHERE username = ?", (username,))
        return cur.fetchone() is not None


# Improvement: Also checks for password_hash
def fetch_user_id(username):
    with open_db() as cur:
        cur.execute("SELECT id FROM users WHERE username = ?", (username,))
        row = cur.fetchone()["id"]
        return row if row else None
    
  
def insert_user(username, password_hash):
    with open_db() as cur:
        cur.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))

  
def fetch_username(user_id):
    with open_db() as cur:
        cur.execute("SELECT username FROM users WHERE id = ?", (user_id,))
        return cur.fetchone()["username"]

def fetch_hash(username):    
    with open_db() as cur:
        cur.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
        return cur.fetchone()["password_hash"]
    
    
# ******* Sessions *******
def fetch_dashboard_summary(day_start, day_end, user_id):
    with open_db() as cur:
        cur.execute("""SELECT 
                    SUM(duration) AS total_duration,
                    COUNT(*) AS total_sessions 
                    FROM sessions WHERE date >= ? AND date < ? AND subject_id IN 
                    (SELECT id FROM subjects WHERE user_id = ?);
                    """, (day_start, day_end, user_id))
        return cur.fetchone()
    
    
def fetch_dashboard(day_start, day_end, user_id):
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
  
  
def insert_session(subject_id, duration):
    with open_db() as cur:
        cur.execute("INSERT INTO sessions (subject_id, duration) VALUES (?, ?)", (subject_id, duration))
        return cur.lastrowid
    
    
def insert_session_topic(session_id, topic_id):
    with open_db() as cur:
        cur.execute("UPDATE sessions SET topic_id = ? WHERE id = ?", (topic_id, session_id))
        
  
# ******* Subjects ********
def subject_exists(subject_name, subject_user_id):
    with open_db() as cur:
        cur.execute("SELECT * FROM subjects WHERE name = ? AND user_id = ?", (subject_name, subject_user_id)) 
        return cur.fetchone() is not None


def fetch_subjects(user_id):
    with open_db() as cur:
        cur.execute("SELECT id, name FROM subjects WHERE user_id = ?", (user_id,))
        return cur.fetchall()
    
def fetch_subject_stats(subject_id):
    with open_db() as cur:
        cur.execute("""SELECT sub.*,
                    (SELECT COUNT(*) FROM topics WHERE subject_id = sub.id) AS topic_count,
                    (SELECT COUNT(*) FROM sessions WHERE subject_id = sub.id) AS session_count,
                    (SELECT SUM(sessions.duration) FROM sessions WHERE subject_id = sub.id) AS total_duration,
                    (SELECT MAX(sessions.date) FROM sessions WHERE subject_id = sub.id) AS last_session_date
                    FROM subjects sub WHERE sub.id = ?""", (subject_id,))       
        return cur.fetchone()                 


def insert_subject(subject_name, subject_user_id):
    with open_db() as cur:
        cur.execute("INSERT INTO subjects (user_id, name) VALUES (?, ?)", (subject_user_id, subject_name))  
        return cur.lastrowid 


def remove_subject(user_id, subject_id):
    with open_db() as cur:
        cur.execute("DELETE FROM subjects WHERE id = ? AND user_id = ?", (subject_id, user_id))

        
def fetch_subject_id(subject_name, user_id):
    with open_db() as cur:
        cur.execute("SELECT id FROM subjects WHERE user_id = ? AND name = ?", (user_id, subject_name))
        row = cur.fetchone()
        return row["id"] if row else None
    
    
# ****** Topics *******
def fetch_topics_stats(subject_id):
    with open_db() as cur:
        cur.execute("SELECT t.*, COUNT(s.id) AS session_count, SUM(s.duration) AS total_duration, MIN(s.date) AS first_session_date FROM topics t LEFT JOIN sessions s ON t.id = s.topic_id WHERE t.subject_id = ? GROUP BY t.id;", (subject_id,))
        return cur.fetchall()
        
    
def topic_exists(topic_name, subject_id):
    with open_db() as cur:
        cur.execute("SELECT * FROM topics WHERE subject_id = ? AND name = ?", (subject_id, topic_name))
        return cur.fetchone() is not None
    
    
def insert_topic(topic_name, subject_id):
    with open_db() as cur:
        cur.execute("INSERT INTO topics (subject_id, name) VALUES (?, ?)", (subject_id, topic_name))
        return cur.lastrowid

def remove_topic(user_id, subject_id, topic_id):
    with open_db() as cur:
        cur.execute("""DELETE FROM topics WHERE id = ? AND subject_id =
                    (SELECT id FROM subjects WHERE id = ? AND user_id = ?)""", (topic_id, subject_id, user_id))
        
        
def fetch_topic_id(topic_name, subject_id):
    with open_db() as cur:
        cur.execute("SELECT id FROM topics WHERE subject_id = ? AND name = ?", (subject_id, topic_name))
        row = cur.fetchone()
        return row["id"] if row else None
    
    
def assign_topic_chapter(topic_id, chapter_id):
    with open_db() as cur:
        cur.execute("UPDATE topics SET chapter_id = ? WHERE id = ?", (chapter_id, topic_id))



# ******** Chapters ********
def fetch_chapters(subject_id):
    with open_db() as cur:
        cur.execute("SELECT * FROM chapters WHERE subject_id = ?", (subject_id,))
        return cur.fetchall()


def chapter_exists(chapter_name, subject_id):
    with open_db() as cur:
        cur.execute("SELECT * FROM chapters WHERE subject_id = ? AND name = ?", (subject_id, chapter_name))
        return cur.fetchone() is not None 
        
def insert_chapter(chapter_name, subject_id):
    with open_db() as cur:
        cur.execute("INSERT INTO chapters (subject_id, name) VALUES (?, ?)", (subject_id, chapter_name))
        

def remove_chapter(user_id, subject_id, chapter_id):
    with open_db() as cur:
        cur.execute("""DELETE FROM chapters WHERE id = ? AND subject_id =
                    (SELECT id FROM subjects WHERE id = ? AND user_id = ?)""", (chapter_id, subject_id, user_id))
        

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
