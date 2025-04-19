import google.generativeai as genai  # Import Google Generative AI library
import os  # Used to access environment variables
from flask import Flask, Blueprint, render_template, request, jsonify  # Flask essentials
from flask_cors import CORS  # Enables CORS (Cross-Origin Resource Sharing)
from dotenv import load_dotenv  # Load environment variables from .env file

# Load environment variables from a .env file into the environment
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Allow requests from other origins (necessary for frontend-backend communication)

# Securely load the Google Generative AI API key from environment variables
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("GOOGLE_API_KEY is missing! Set it in the environment variables.")
genai.configure(api_key=API_KEY)  # Configure the Generative AI API using the key

# Initialize the Generative AI model
model = genai.GenerativeModel("models/gemini-1.5-flash")  # Load the Gemini AI model

# Create a blueprint for tool2 feature (modular code structure)
tool2_bp = Blueprint("tool2", __name__, url_prefix="/tool2", template_folder="templates")

# Store chats in memory — for production, use a database like DynamoDB
chats = [{'name': 'New Chat', 'id': 1, 'messages': []}]  # Initial chat setup

# Function to generate AI response based on user prompt and chat history
def AIResponse(prompt, chat_history=None):
    if chat_history:
        # Build chat context from history for better responses
        context = "\n".join(
            [f"User: {msg['text']}" if msg['text'].startswith('User') else f"AI: {msg['text']}" for msg in chat_history]
        )
        prompt = f"{context}\nUser: {prompt}\nAI:"  # Add current prompt to context
    
    try:
        response = model.generate_content(prompt)  # Get AI-generated response
        return response.text  # Return text portion
    except Exception as e:
        return f"Error generating response: {str(e)}"  # Return error if exception occurs

# Route for rendering the main chatbot UI (tool2 interface)
@tool2_bp.route('/')
def tool2_index():
    print("Accessed /tool2/ route")  # Debug log for route access
    return render_template('bot.html')  # Render the chatbot HTML page

# Route to return list of all chat sessions
@tool2_bp.route("/get_chats", methods=['GET'])
def get_chats():
    print("Accessed /tool2/get_chats route")  # Debug log
    return jsonify({'chats': chats})  # Return chats as JSON

# Route to fetch the chat history for a given chat_id
@tool2_bp.route("/get_chat_history", methods=['GET'])
def get_chat_history():
    print("Accessed /tool2/get_chat_history route")  # Debug log
    chat_id = int(request.args.get('chat_id'))  # Get chat_id from query parameter
    chat = next((chat for chat in chats if chat['id'] == chat_id), None)  # Find chat by ID
    return jsonify({'messages': chat['messages']} if chat else {'messages': []})  # Return messages or empty list

# Route to generate AI response from user input
@tool2_bp.route('/generate', methods=['POST'])
def generate():
    print("Accessed /tool2/generate route")  # Debug log
    data = request.get_json()  # Get JSON data from request
    user_input = data.get('input', '').strip()  # Extract and clean user input
    chat_id = data.get('chat_id')  # Extract chat ID

    if not user_input:
        return jsonify({'error': 'User input is required'}), 400  # Error if no input

    chat = next((chat for chat in chats if chat['id'] == chat_id), None)  # Find chat by ID
    chat_history = chat['messages'] if chat else []  # Get chat history if chat exists

    response = AIResponse(user_input, chat_history)  # Get AI-generated response

    if chat:
        chat['messages'].append({'text': f'User: {user_input}'})  # Save user message
        chat['messages'].append({'text': f'AI: {response}'})  # Save AI response

    return jsonify({'response': response})  # Return the AI response

# Route to create a new chat session
@tool2_bp.route('/new_chat', methods=['POST'])
def new_chat():
    print("Accessed /tool2/new_chat route")  # Debug log
    data = request.get_json()  # Get data from request
    chat_name = data.get('chat_name', '').strip()  # Get and clean chat name
    if not chat_name:
        return jsonify({'error': 'Chat name is required'}), 400  # Error if name is missing

    new_chat_id = len(chats) + 1  # Generate new unique chat ID
    new_chat = {'name': chat_name, 'id': new_chat_id, 'messages': []}  # Create new chat dict
    chats.append(new_chat)  # Add new chat to list
    return jsonify({'status': 'Chat created successfully', 'chat_id': new_chat_id})  # Return success response

# Route to delete a specific chat session
@tool2_bp.route('/delete_chat', methods=['POST'])
def delete_chat():
    print("Accessed /tool2/delete_chat route")  # Debug log
    data = request.get_json()  # Get request data
    chat_id = data.get('chat_id')  # Extract chat ID
    global chats  # Access global chats list
    chats = [chat for chat in chats if chat['id'] != chat_id]  # Remove chat by filtering
    return jsonify({'status': f'Chat {chat_id} deleted successfully'})  # Return status

# Register the blueprint with the main Flask app
app.register_blueprint(tool2_bp)

# Run the Flask app (debug=True enables live reloading and better error messages)
if __name__ == '__main__':
    app.run(debug=True)
