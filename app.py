from flask import Flask, render_template, request, jsonify
import joblib

app = Flask(__name__)

# Load the trained model
model = joblib.load('mental_health_chatbot_model.pkl')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    user_input = request.json['user_input']
    response = model.predict([user_input])[0]
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)
