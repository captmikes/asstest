
import json
from datetime import datetime
from flask import Flask, request, jsonify, g
import openai

app = Flask(__name__)

# Load configuration settings
with open('config.json') as config_file:
    config = json.load(config_file)

openai.api_key = config.get('openai_api_key')  # Ensure the API key is stored securely

@app.before_request
def load_previous_session():
    try:
        with open(config['knowledge_file_path'], 'r') as knowledge_file:
            g.session_data = json.load(knowledge_file)
    except FileNotFoundError:
        g.session_data = {"sessions": []}

@app.after_request
def save_session_summary(response):
    session_summary = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_input": request.get_json(),
        "response": response.get_json()
    }
    g.session_data["sessions"].append(session_summary)
    with open(config['knowledge_file_path'], 'w') as knowledge_file:
        json.dump(g.session_data, knowledge_file, indent=4)
    return response

@app.route('/process_text', methods=['POST'])
def process_text():
    user_input = request.json.get('text')
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=user_input,
        max_tokens=150
    )
    return jsonify({"response": response.choices[0].text})

@app.route('/process_image', methods=['POST'])
def process_image():
    image_file = request.files['image']
    response = openai.Image.create(
        model="image-gpt-4",
        files={"file": image_file},
        user_task="Describe"
    )
    return jsonify({"description": response.choices[0].text})

if __name__ == '__main__':
    app.run(debug=True)
