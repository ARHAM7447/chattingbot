import google.generativeai as genai
import os
from flask import Blueprint, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create Blueprint for tool1
tool1_bp = Blueprint("tool1", __name__, url_prefix="/tool1", template_folder="templates")
CORS(tool1_bp)

# Retrieve API Key securely
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY is missing! Set it in .env file.")

# Configure Google Generative AI
genai.configure(api_key=api_key)

# Initialize AI Model
model = genai.GenerativeModel("gemini-1.5-pro")  # Fixed model name

# Global conversation history
conversation_history = []

# Voice Assistance Function
def voice_assistance(user_input):
    global conversation_history

    prompt = f"""
    You are an AI assistant in an engaging conversation with a user. The user just asked:
    '{user_input}'
    Provide a direct and informative answer, avoiding unnecessary elaboration.
    """
    try:
        response_obj = model.generate_content(prompt)
        response = response_obj.text if response_obj else "No response from AI."
    except Exception as e:
        print(f"Error in model generation: {str(e)}")
        return "Sorry, I couldn't process your request at the moment."

    # Store conversation history
    conversation_history.append({"user": user_input, "ai": response})
    return response


# Route for AI Chat Page
@tool1_bp.route("/")
def home():
    return render_template("tool1/chat.html")  # Ensure this file exists


# Route to Process Voice Input
@tool1_bp.route("/process_voice", methods=["POST"])
def process_voice():
    try:
        user_input = request.json.get("user_input")
        print(f"Received user input: {user_input}")  # Debugging

        if not user_input:
            return jsonify({"error": "No user input provided"}), 400

        # Generate AI response
        response = voice_assistance(user_input)
        print(f"AI Response: {response}")

        return jsonify({"response": response, "conversation_history": conversation_history})

    except Exception as e:
        print(f"Error occurred in processing voice: {str(e)}")
        return jsonify({"error": "An error occurred while processing the request"}), 500
