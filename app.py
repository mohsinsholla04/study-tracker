from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from db import *
from helpers import *
from datetime import datetime

app = Flask(__name__)


app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] ="filesystem"
Session(app)


@app.route("/")
# Shows dashboard 
def index():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")
    
    today_stats_summary, today_stats = get_dashboard_stats(1, user_id)
    week_stats_summary, week_stats = get_dashboard_stats(7, user_id)
    month_stats_summary, month_stats = get_dashboard_stats(30, user_id)
    
    return render_template("index.html", username=fetch_username(user_id), today_stats_summary=today_stats_summary, today_stats=today_stats, week_stats_summary=week_stats_summary, week_stats=week_stats, month_stats_summary=month_stats_summary, month_stats=month_stats)


@app.route("/subjects")
def subjects():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")
    
    subjects = fetch_subjects(user_id)
    return render_template("subjects.html", subjects=subjects)


@app.route("/subjects/<int:subject_id>")
def subject(subject_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")
    
    subject = get_subject_stats(subject_id)
    chapters = fetch_chapters(subject_id) 
    grouped_topics, ungrouped_topics= get_topics_stats(subject_id)
    
    return render_template("subject.html", subject=subject, chapters=chapters, grouped_topics=grouped_topics, ungrouped_topics=ungrouped_topics)


@app.route("/subjects/add", methods=["POST"])
def add_subject():
    user_id = session.get("user_id")
    if not user_id:
       return redirect("/login")
    
    subject_name = request.form.get("subject_name")
    if not subject_name:
        return render_template("error.html", msg="Subject not entered")
    
    if subject_exists(subject_name, user_id):
        return render_template("error.html", msg="Subject already exists")
    
    insert_subject(subject_name, user_id)
    
    return redirect("/subjects")

@app.route("/subjects/<int:subject_id>/delete", methods=["POST"])
def delete_subject(subject_id):
    remove_subject(subject_id)
    return redirect("/subjects")


@app.route("/subjects/<int:subject_id>/topics/add", methods=["POST"])
def add_topic(subject_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")
    
    topic_name = request.form.get("topic_name")
    if not topic_name:
        return render_template("error.html", msg="Topic not entered")
    
    if topic_exists(topic_name, subject_id):
        return render_template("error.html", msg="Topic already exists")
    
    insert_topic(topic_name, subject_id)
    
    return redirect(f"/subjects/{subject_id}")  
    
    
@app.route("/<int:subject_id>/topics/<int:topic_id>/delete", methods=["POST"])
def delete_topic(subject_id, topic_id):
    remove_topic(topic_id)
    return redirect(f"/subjects/{subject_id}")


@app.route("/subjects/<int:subject_id>/chapters/add", methods=["POST"])
def add_chapter(subject_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")
    
    chapter_name = request.form.get("chapter_name")
    if not chapter_name:
        return render_template("error.html", msg="Chapter not entered")
    
    if chapter_exists(chapter_name, subject_id):
        return render_template("error.html", msg="Chapter already exists")
    
    insert_chapter(chapter_name, subject_id)
    
    return redirect(f"/subjects/{subject_id}") 
    
  
@app.route("/<int:subject_id>/chapters/<int:chapter_id>/delete", methods=["POST"])
def delete_chapter(subject_id, chapter_id):
    remove_chapter(chapter_id)
    return redirect(f"/subjects/{subject_id}")  


@app.route("/chapters/<int:chapter_id>/assign-topic", methods=["POST"])
def assign_topic(chapter_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")
    
    topic_id = request.form.get("topic_id")
    subject_id = request.form.get("subject_id")
       
    assign_topic_chapter(topic_id, chapter_id)
    return redirect(f"/subjects/{subject_id}") 
    

@app.route("/create-session", methods=["GET", "POST"])
def create_session():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")
    
    if request.method == "GET":
        return render_template("session.html")
    
    # Get subject_id if subject does not exist create it 
    subject_name = request.form.get("subject_name")
    if not subject_name:
        return redirect("/")
    subject_id = fetch_subject_id(subject_name, user_id)
    if subject_id is None:
        insert_subject(subject_name, user_id)
        subject_id = fetch_subject_id(subject_name, user_id)
        
    try:
        duration = int(request.form.get("duration"))
    except ValueError:
        return redirect("/")
    
    topic_name = request.form.get("topic_name")
    session_id = insert_session(subject_id, duration)
    if not topic_name:
        return redirect("/") 
    
    # Get topic_id if topic does not exist create it 
    topic_id = fetch_topic_id(topic_name, subject_id)
    if topic_id is None:
        insert_topic(topic_name, subject_id)
        topic_id = fetch_topic_id(topic_name, subject_id)
    
    # Link them
    insert_session_topic(session_id, topic_id)
        
    return redirect("/")
    

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html", task="Register")
    
    username = request.form.get("username").strip()
    password = request.form.get("password").strip()
    confirm_pass = request.form.get("confirm_pass").strip()
        
    # Validate the inputs
    if not username:
        return render_template("error.html", msg="Username Not Entered")
        
    if len(password) < 8: 
        return render_template("error.html", msg="Password is too short")
        
    if password != confirm_pass:
        return render_template("error.html", msg="Password and confirm password do not match")
        
    if username_exists(username):
        return render_template("error.html", msg="Username already exists")
        
    register_user(username, password)

    return redirect("/login")
    


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    
    username = request.form.get("username")
    password = request.form.get("password")
        
    if not username or not password:
        return render_template("error.html", msg="Username Or Password Not Entered")
    if not check_user(username, password):
        return render_template("error.html", msg="Incorrect Credentials")
        
    session["user_id"] = fetch_user_id(username) 
    return redirect("/")
        


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

        
if __name__ == "__main__":
    init_db()
    app.run(debug=True)