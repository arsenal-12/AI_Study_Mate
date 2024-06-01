from flask import Flask, render_template,send_from_directory
import subprocess
import os
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_crossword')
def start_crossword():
    # Execute your Python script here
    # Example: 
    subprocess.Popen(['python', 'ChillZone-main\crossword_puzzle-1.1.44\crossword_puzzle-1.1.44\src\main.py'])
@app.route('/crackcode')
def crack_code():
    return render_template('crackcode.html')
@app.route('/memorygame')
def memory_game():
    return render_template('memorygame.html')
@app.route('/riddles')
def riddles():
    return render_template('riddles.html')
@app.route('/joke')
def joke():
    return render_template('joke.html')

if __name__ == '__main__':
    app.run(debug=True)
