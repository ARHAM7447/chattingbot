# Import necessary modules
from flask import Blueprint, render_template, request  # Flask components for routing and rendering
import google.generativeai as genai  # Google's Gemini AI SDK
import os  # For accessing environment variables
import PyPDF2  # For reading PDF files
from dotenv import load_dotenv  # For loading variables from .env file

# Load all environment variables from the .env file
load_dotenv()

# Define a Blueprint for tool7 - this makes it modular and easy to plug into the main app
tool7_bp = Blueprint("tool7", __name__, template_folder="templates")

# Get the Google API key securely from environment variables
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    # Raise an error if the key is missing
    raise ValueError("Google API Key is missing. Please set it in the .env file.")

# Configure the Gemini model using the API key
genai.configure(api_key=api_key)

# Initialize the generative model (Gemini 1.5 Flash)
model = genai.GenerativeModel("gemini-1.5-flash")

# Function to classify text as real or scam email
def predict_fake_or_real_email_content(text):
    # Prompt instructing the model to detect scam/legitimate messages
    prompt = f"""
    You are an expert in identifying scam messages. Analyze the given text and classify it as:

    - **Real/Legitimate**
    - **Scam/Fake**

    Text:
    {text}

    Return only the classification and a brief reason.
    """
    try:
        # Generate a response from the model
        response = model.generate_content(prompt)
        # Return the model's text result, stripped of extra spaces
        return response.text.strip() if response else "Classification failed."
    except Exception as e:
        # Return error message in case of failure
        return f"Error: {str(e)}"

# Function to classify a URL as phishing, malware, etc.
def url_detection(url):
    # Prompt instructing the model to analyze the URL
    prompt = f"""
    Classify the following URL:
    - **Benign** (Safe)
    - **Phishing** (Fraud)
    - **Malware** (Malicious)
    - **Defacement** (Hacked)

    URL: {url}
    """
    try:
        # Get response from the model
        response = model.generate_content(prompt)
        # Return the result in lowercase
        return response.text.strip().lower() if response else "Detection failed."
    except Exception as e:
        # Return error message if generation fails
        return f"Error: {str(e)}"

# Route to show the homepage/form page
@tool7_bp.route('/')
def home():
    # Render the main tool7.html page
    return render_template("tool7.html")

# Route to handle scam detection based on uploaded files
@tool7_bp.route('/scam/', methods=['POST'])
def detect_scam():
    # Check if the user uploaded a file
    if 'file' not in request.files:
        return render_template("tool7.html", message="No file uploaded.")

    file = request.files['file']  # Get the uploaded file
    extracted_text = ""  # Initialize extracted text

    try:
        # If the uploaded file is a PDF
        if file.filename.endswith('.pdf'):
            pdf_reader = PyPDF2.PdfReader(file)  # Read the PDF
            # Extract text from all pages
            extracted_text = " ".join([page.extract_text() or '' for page in pdf_reader.pages])
        # If it's a TXT file
        elif file.filename.endswith('.txt'):
            # Read and decode the text file
            extracted_text = file.read().decode("utf-8")
        else:
            # Show error for unsupported file types
            return render_template("tool7.html", message="Invalid file type. Please upload a PDF or TXT file.")

        # Check if the file is empty or failed to extract any text
        if not extracted_text.strip():
            return render_template("tool7.html", message="File is empty or text could not be extracted.")

        # Use AI model to analyze and classify the extracted text
        message = predict_fake_or_real_email_content(extracted_text)
        return render_template("tool7.html", message=message)

    except Exception as e:
        # Handle unexpected errors during processing
        return render_template("tool7.html", message=f"Error processing file: {str(e)}")

# Route to handle URL classification
@tool7_bp.route('/predict', methods=['POST'])
def predict_url():
    # Get the URL entered by the user from the form
    url = request.form.get('url', '').strip()

    # Check if the URL starts with http:// or https://
    if not url.startswith(("http://", "https://")):
        return render_template("tool7.html", message="Invalid URL format.", input_url=url)

    # Classify the URL using AI model
    classification = url_detection(url)
    # Render the result back to the same page
    return render_template("tool7.html", input_url=url, predicted_class=classification)
