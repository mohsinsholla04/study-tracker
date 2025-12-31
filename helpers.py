from werkzeug.security import generate_password_hash, check_password_hash
from db import *
from datetime import date, timedelta, datetime

    

def register_user(username, password):
    password_hash = generate_password_hash(password)
    insert_user(username, password_hash)
    
    
def check_user(username, password):
    if not username_exists(username):
        return False
    password_hash = fetch_hash(username)
    if not check_password_hash(password_hash, password):
        return False
    return True


def get_dashboard_stats(no_days, user_id):
    today_start = date.today()
    # To check for today
    if no_days == 1:
        start = datetime.combine(today_start, datetime.min.time())
        end = start + timedelta(days=no_days)
    else:
        # To check for past no_days "days" 
        end = datetime.combine(today_start, datetime.min.time()) 
        start = end - timedelta(days=no_days) 
    stats_summary = fetch_dashboard_summary(start, end, user_id)
    stats = fetch_dashboard(start, end, user_id)
    return stats_summary, stats


def get_subject_stats(subject_id):
    subject = fetch_subject_stats(subject_id)
    subject = dict(subject)
    if subject["last_session_date"]:
        subject["last_session_date"] = datetime.strptime(subject["last_session_date"],  "%Y-%m-%d %H:%M:%S")
    return subject


def get_topics_stats(subject_id):
    topics = [dict(topic) for topic in fetch_topics_stats(subject_id)]
    for topic in topics:
        if topic["first_session_date"]:
            topic["first_session_date"] = datetime.strptime(topic["first_session_date"], "%Y-%m-%d %H:%M:%S")
            
    grouped_topics, ungrouped_topics = seperate_topics(topics)
    return grouped_topics, ungrouped_topics


def seperate_topics(topics):
    grouped_topics = []
    ungrouped_topics = []
    for topic in topics:
        if topic["chapter_id"] is None:
            ungrouped_topics.append(topic)
        else:
            grouped_topics.append(topic)
    return grouped_topics, ungrouped_topics