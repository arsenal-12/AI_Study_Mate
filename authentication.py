from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from bs4 import BeautifulSoup
import requests
from transformers import pipeline
from youtube_transcript_api import YouTubeTranscriptApi

def summarize_youtube_video(youtube_video):
    try:
        # Extract the video ID from the URL
        video_id = youtube_video.split("v=")[1]

        # Fetch the video transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id)

        # Combine the transcript text into a single string
        result = " ".join([item['text'] for item in transcript])

        # Initialize the summarizer pipeline
        summarizer = pipeline('summarization', model = "sshleifer/distilbart-cnn-12-6")

        # Split the text into chunks of up to 1000 characters each
        chunk_size = 1000
        chunks = [result[i:i + chunk_size] for i in range(0, len(result), chunk_size)]

        # Summarize each chunk
        summarized_text = []
        for chunk in chunks:
            summary = summarizer(chunk, max_length=150, min_length=50, do_sample=False)
            summary_text = summary[0]['summary_text']
            summarized_text.append(summary_text)

        # Combine summarized chunks into a single string
        final_summary = " ".join(summarized_text)
        return final_summary
    except Exception as e:
        return str(e)


app = Flask(__name__)
app.secret_key = 'team30'  # Change this to a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mobile = db.Column(db.String(15), unique=True, nullable=False)
    study_class = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(60), nullable=False)

# Define subjects for each day
schedule = {
    "Monday": ["CDSS", "LIBRARY", "TEA BREAK", "CDSS LAB FOR D1 && CN LAB FOR D2", "LUNCH BREAK", "BLOCK CHAIN"],
    "Tuesday": ["CC", "CDSS", "TEA BREAK", "CRYPTOGRAPHY","CRYPTOGRAPHY", "LUNCH BREAK", "DEEP LEARNING", "CN"],
    "Wednesday": ["CDSS LAB FOR D2 && CN LAB FOR D1","CDSS LAB FOR D2 && CN LAB FOR D1", "TEA BREAK", "CC", "LIBRARY", "LUNCH BREAK", "BLOCK CHAIN"],
    "Thursday": ["LIBRARY", "CN", "TEA BREAK", "LIBRARY", "CDSS", "LUNCH BREAK", "DEEP LEARNING", "CRYPTOGRAPHY"],
    "Friday": ["CN", "CDSS", "TEA BREAK", "LIBRARY", "CC"],
    "Saturday": [],
    "Sunday": []  # No schedule on Sunday
}

NPTEL_URL = 'https://nptel.ac.in/course.html'

def fetch_nptel_courses(domain):
    try:
        # Construct the URL with query parameters
        url = f'{NPTEL_URL}?discipline={domain}'

        # Make a request to NPTEL website
        response = requests.get(url)

        # Check if request was successful
        if response.status_code == 200:
            # Parse the HTML content to extract course information
            soup = BeautifulSoup(response.content, 'html.parser')
            courses = []

            # Example parsing
            for course_elem in soup.find_all('div', class_='course'):
                title = course_elem.find('h2').text.strip()
                description = course_elem.find('p').text.strip()
                link = course_elem.find('a')['href']
                courses.append({'title': title, 'description': description, 'link': link})

            # Return courses
            return courses
        else:
            return []
    except Exception as e:
        print(f"An error occurred while fetching NPTEL courses: {str(e)}")
        return []

@app.route('/fetch_courses', methods=['POST'])
def fetch_courses():
    domain = request.form['domain']
    courses = fetch_nptel_courses(domain)
    return render_template('links.html', domain=domain, courses=courses)

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/subjects')
def subjects():
    return render_template('subjects.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        mobile = request.form['mobile']
        study_class = request.form['study_class']
        password = request.form['password']
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, mobile=mobile, study_class=study_class, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            flash('Login successful', 'success')
            return redirect(url_for('subjects'))
        else:
            flash('Login failed. Check your email and password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    flash('Logged out successfully', 'info')
    return redirect(url_for('login'))

@app.route('/craft')
def craft():
    return render_template('craft.html')

@app.route('/mynotes')
def mynotes():
    return render_template('mynotes.html')

@app.route('/chatbot.html')
def chatbot():
    return render_template('chatbot.html')
# Route to serve all subjects
@app.route('/chatbots/<subject>')
def subject(subject):
    return render_template('chatbots/cloud_computing.html')

@app.route('/quiz.html')
def quiz():
    return render_template('quiz.html')  

@app.route('/game.html')
def game():
    return render_template('game.html')

@app.route('/Cuenote.html')
def cuenotes():
    return render_template('Cuenote.html')

@app.route('/video')
def video():
    return render_template('index.html')

@app.route('/generate_summary', methods=['POST'])
def generate_summary():
    data = request.get_json()
    video_url = data.get('video_url')
    summary = summarize_youtube_video(video_url)
    return jsonify({'summary': summary})

@app.route('/links')
def links():
    return render_template('links.html')

@app.route('/work_remainder')
def work_remainder():
    return render_template('work_remainder.html')

@app.route('/fetch_nptel_courses', methods=['GET'])
def fetch_nptel_courses_api():
    domain = request.args.get('domain')

    # Fetch NPTEL courses
    courses = fetch_nptel_courses(domain)

    # Return courses as JSON response
    return jsonify(courses)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
