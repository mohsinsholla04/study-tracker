from werkzeug.security import generate_password_hash, check_password_hash
from db import *
from datetime import date, timedelta, datetime

    

def register_user(username, password):
    password_hash = generate_password_hash(password)
    add_user(username, password_hash)
    
    
def check_user(username, password):
    if not username_exists(username):
        return False
    password_hash = get_hash(username)
    if not check_password_hash(password_hash, password):
        return False
    return True


def seperate_topics(topics):
    grouped_topics = []
    ungrouped_topics = []
    for topic in topics:
        if topic["chapter_id"] is None:
            ungrouped_topics.append(topic)
        else:
            grouped_topics.append(topic)
    return grouped_topics, ungrouped_topics


def get_verified_subject_id(subject_name, user_id):
    if subject_exists(subject_name, user_id):
        return get_subject_id(subject_name, user_id)
    
    add_subject_db(subject_name, user_id)
    return get_subject_id(subject_name, user_id)


def get_verified_topic_id(topic_name, subject_id):
    if topic_exists(topic_name, subject_id):
        return get_topic_id(topic_name, subject_id)
    
    add_topic_db(topic_name, subject_id)
    return get_topic_id(topic_name, subject_id)


def topics_dates_fixer(topics):
    topics = [dict(topic) for topic in topics]
    for topic in topics:
        if topic["first_session_date"]:
            topic["first_session_date"] = datetime.strptime(topic["first_session_date"], "%Y-%m-%d %H:%M:%S")
    return topics


def get_today_stats(user_id):
    todays_date = date.today()
    start = datetime.combine(todays_date, datetime.min.time())
    end = start + timedelta(days=1)
    today_stats_summary = get_dashboard_summary(start, end, user_id)
    today_stats = get_dashboard_details(start, end, user_id)
    return today_stats_summary, today_stats


def get_week_stats(user_id):
    todays_date = date.today()
    end = datetime.combine(todays_date, datetime.min.time())
    start = end - timedelta(days=7)
    week_stats_summary = get_dashboard_summary(start, end, user_id)
    week_stats = get_dashboard_details(start, end, user_id)
    return week_stats_summary, week_stats


def get_month_stats(user_id):
    todays_date = date.today()
    end = datetime.combine(todays_date, datetime.min.time())
    start = end - timedelta(days=30)
    month_stats_summary = get_dashboard_summary(start, end, user_id)
    month_stats = get_dashboard_details(start, end, user_id)
    return month_stats_summary, month_stats