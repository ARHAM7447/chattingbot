from flask import Blueprint, render_template, request
import google.generativeai as genai
import os
import PyPDF2
from dotenv import load_dotenv  

# Load environment variables
load_dotenv()

tool7_bp = Blueprint("tool7", __name__, template_folder="templates")

# Get Google API Key securely
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("Google API Key is missing. Please set it in the .env file.")

# Configure Google AI model
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# Function to classify email content
def predict_fake_or_real_email_content(text):
    prompt = f"""
    You are an expert in identifying scam messages. Analyze the given text and classify it as:

    - **Real/Legitimate**
    - **Scam/Fake**

    Text:
    {text}

    Return only the classification and a brief reason.
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip() if response else "Classification failed."
    except Exception as e:
        return f"Error: {str(e)}"

# Function to classify URLs
def url_detection(url):
    prompt = f"""
    Classify the following URL:
    - **Benign** (Safe)
    - **Phishing** (Fraud)
    - **Malware** (Malicious)
    - **Defacement** (Hacked)

    URL: {url}
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip().lower() if response else "Detection failed."
    except Exception as e:
        return f"Error: {str(e)}"

# Flask Routes
@tool7_bp.route('/')
def home():
    return render_template("tool7.html")

@tool7_bp.route('/scam/', methods=['POST'])
def detect_scam():
    if 'file' not in request.files:
        return render_template("tool7.html", message="No file uploaded.")

    file = request.files['file']
    extracted_text = ""

    try:
        if file.filename.endswith('.pdf'):
            pdf_reader = PyPDF2.PdfReader(file)
            extracted_text = " ".join([page.extract_text() or '' for page in pdf_reader.pages])
        elif file.filename.endswith('.txt'):
            extracted_text = file.read().decode("utf-8")
        else:
            return render_template("tool7.html", message="Invalid file type. Please upload a PDF or TXT file.")

        if not extracted_text.strip():
            return render_template("tool7.html", message="File is empty or text could not be extracted.")

        message = predict_fake_or_real_email_content(extracted_text)
        return render_template("tool7.html", message=message)
    except Exception as e:
        return render_template("tool7.html", message=f"Error processing file: {str(e)}")

@tool7_bp.route('/predict', methods=['POST'])
def predict_url():
    url = request.form.get('url', '').strip()

    if not url.startswith(("http://", "https://")):
        return render_template("tool7.html", message="Invalid URL format.", input_url=url)

    classification = url_detection(url)
    return render_template("tool7.html", input_url=url, predicted_class=classification)