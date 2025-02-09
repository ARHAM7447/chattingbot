import google.generativeai as genai
import os
from flask import Blueprint, render_template, request, jsonify
from difflib import SequenceMatcher
from flask_cors import CORS
# Create Blueprint for tool1
tool1_bp = Blueprint('tool1', __name__, url_prefix='/tool1', template_folder='templates')
CORS(tool1_bp)  # Enable CORS for the tool1 Blueprint
# Set up Google API key securely
os.environ["GOOGLE_API_KEY"] = "AIzaSyA9Td4VAH9p6mfAiSVgEUa4N7zxwIou_5U"  # 🔒 Replace with secure method
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# Initialize AI Model
model = genai.GenerativeModel("models/gemini-1.5-pro")

# Global conversation history
conversation_history = []

# Voice assistance function
def voice_assistance(user_input):
    global conversation_history

    prompt = f"""
    You are an AI assistant in an engaging conversation with a user. The user just asked:
    '{user_input}'
    Provide a direct and informative answer, avoiding unnecessary elaboration.
    """

    try:
        response = model.generate_content(prompt).text
        print(f"Generated response: {response}")  # Log the generated response
    except Exception as e:
        print(f"Error in model generation: {str(e)}")
        return "Sorry, I couldn't process your request at the moment."

    # Store conversation history
    conversation_history.append({'user': user_input, 'ai': response})

    return response


# Route for AI chat page
@tool1_bp.route('/')
def home():
    return render_template('tool1/chat.html')  # ✅ Correct path to chat.html

# Route to handle voice input and return AI response
@tool1_bp.route('/process_voice', methods=['POST'])
def process_voice():
    try:
        user_input = request.json.get("user_input")
        print(f"Received user input: {user_input}")  # Log the input

        if not user_input:
            print("Error: No user input provided")
            return jsonify({'error': 'No user input provided'}), 400

        # Log the start of AI processing
        print("Processing AI response...")
        response = voice_assistance(user_input)
        print(f"AI Response: {response}")  # Log the AI response

        return jsonify({'response': response, 'conversation_history': conversation_history})

    except Exception as e:
        print(f"Error occurred in processing voice: {str(e)}")
        return jsonify({'error': 'An error occurred while processing the request'}), 500
