import google.generativeai as genai
import os
from flask import Flask, Blueprint, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv  # Securely load environment variables

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for the entire app

# Set up Google Generative AI API Key securely
API_KEY = os.getenv("GOOGLE_API_KEY")  # Load from .env or environment variables
if not API_KEY:
    raise ValueError("GOOGLE_API_KEY is missing! Set it in the environment variables.")
genai.configure(api_key=API_KEY)

# Initialize AI model
model = genai.GenerativeModel("models/gemini-pro")

# Blueprint for Tool2
tool2_bp = Blueprint("tool2", __name__, url_prefix="/tool2", template_folder="templates")

# Store chats in memory (use database in production)
chats = [{'name': 'New Chat', 'id': 1, 'messages': []}]  # Default first chat

# AI Response Function
def AIResponse(prompt, chat_history=None):
    if chat_history:
        context = "\n".join(
            [f"User: {msg['text']}" if msg['text'].startswith('User') else f"AI: {msg['text']}" for msg in chat_history]
        )
        prompt = f"{context}\nUser: {prompt}\nAI:"
    
    response = model.generate_content(prompt)
    return response.text

# Tool2 Routes (inside Blueprint)
@tool2_bp.route('/')
def tool2_index():
    return render_template('bot.html')  # Ensure this file exists in `templates/tool2/`

@tool2_bp.route("/get_chats", methods=['GET'])
def get_chats():
    return jsonify({'chats': chats})

@tool2_bp.route("/get_chat_history", methods=['GET'])
def get_chat_history():
    chat_id = int(request.args.get('chat_id'))
    chat = next((chat for chat in chats if chat['id'] == chat_id), None)
    return jsonify({'messages': chat['messages']} if chat else {'messages': []})

@tool2_bp.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    user_input = data.get('input')
    chat_id = data.get('chat_id')

    chat = next((chat for chat in chats if chat['id'] == chat_id), None)
    chat_history = chat['messages'] if chat else []

    response = AIResponse(user_input, chat_history)

    if chat:
        chat['messages'].append({'text': f'User: {user_input}'})
        chat['messages'].append({'text': f'AI: {response}'})

    return jsonify({'response': response})

@tool2_bp.route('/new_chat', methods=['POST'])
def new_chat():
    data = request.get_json()
    chat_name = data.get('chat_name')
    new_chat_id = len(chats) + 1
    new_chat = {'name': chat_name, 'id': new_chat_id, 'messages': []}
    chats.append(new_chat)
    return jsonify({'status': 'Chat created successfully', 'chat_id': new_chat_id})

@tool2_bp.route('/delete_chat', methods=['POST'])
def delete_chat():
    data = request.get_json()
    chat_id = data.get('chat_id')
    global chats
    chats = [chat for chat in chats if chat['id'] != chat_id]
    return jsonify({'status': f'Chat {chat_id} deleted successfully'})

# Register Blueprint for Tool2
app.register_blueprint(tool2_bp)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
