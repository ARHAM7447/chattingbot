# Import the Google Generative AI SDK
import google.generativeai as genai

# Import os module to access environment variables
import os

# Import required Flask modules
from flask import Blueprint, render_template, request, jsonify

# Import CORS to allow cross-origin requests
from flask_cors import CORS

# Import load_dotenv to read variables from .env file
from dotenv import load_dotenv

# Load environment variables from a .env file into the environment
load_dotenv()

# Create a Flask Blueprint for tool1 with a URL prefix and template folder
tool1_bp = Blueprint("tool1", __name__, url_prefix="/tool1", template_folder="templates")

# Enable CORS on the Blueprint to allow frontend calls from different origins
CORS(tool1_bp)

# Get the Google API key from environment variables
api_key = os.getenv("GOOGLE_API_KEY")

# Raise an error if the API key is not found
if not api_key:
    raise ValueError("GOOGLE_API_KEY is missing! Set it in .env file.")

# Configure the genai library with the provided API key
genai.configure(api_key=api_key)

# Initialize the AI model (using the Gemini 1.5 Pro model)
model = genai.GenerativeModel("gemini-1.5-pro")  # Fixed model name

# Define a global variable to store the conversation history between the user and the AI
conversation_history = []

# Define a function to handle user input and get a voice-based AI response
def voice_assistance(user_input):
    global conversation_history  # Access global conversation history list

    # Define the prompt to instruct the AI to give a clear and concise answer
    prompt = f"""
    You are an AI assistant in an engaging conversation with a user. The user just asked:
    '{user_input}'
    Provide a direct and informative answer, avoiding unnecessary elaboration.
    """

    try:
        # Generate a response using the AI model
        response_obj = model.generate_content(prompt)

        # Extract the actual text from the response object, or show fallback text
        response = response_obj.text if response_obj else "No response from AI."
    except Exception as e:
        # Print the error for debugging if AI fails to generate content
        print(f"Error in model generation: {str(e)}")
        return "Sorry, I couldn't process your request at the moment."

    # Save the user's question and AI's response in the history
    conversation_history.append({"user": user_input, "ai": response})

    # Return the AI's response to the user
    return response

# Define a route to render the chat page
@tool1_bp.route("/")
def home():
    return render_template("tool1/chat.html")  # Load the HTML page for tool1 chat

# Define a route to process voice input from the frontend
@tool1_bp.route("/process_voice", methods=["POST"])
def process_voice():
    try:
        # Get the user's voice input sent as JSON from the frontend
        user_input = request.json.get("user_input")
        print(f"Received user input: {user_input}")  # Debugging

        # If no input is provided, return an error response
        if not user_input:
            return jsonify({"error": "No user input provided"}), 400

        # Call the AI function to generate a response
        response = voice_assistance(user_input)
        print(f"AI Response: {response}")  # Debugging

        # Return the response and full conversation history as JSON
        return jsonify({"response": response, "conversation_history": conversation_history})

    except Exception as e:
        # Print the error and return an error response if anything goes wrong
        print(f"Error occurred in processing voice: {str(e)}")
        return jsonify({"error": "An error occurred while processing the request"}), 500
