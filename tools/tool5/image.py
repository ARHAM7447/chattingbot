# Import required libraries
from flask import Blueprint, render_template, request, jsonify  # Flask utilities
from PyPDF2 import PdfReader  # For reading and extracting text from PDF files
import google.generativeai as genai  # Google Gemini for AI content generation
import os  # For environment variable handling
import json  # To handle JSON parsing
import re  # For regular expressions to extract JSON from text

# Set your API key as an environment variable (for Gemini AI)
os.environ["GOOGLE_API_KEY"] = "AIzaSyCS_vlMLsisM9_VbzflZzkzgBEbqc4tzyg"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])  # Configure the Gemini API

# Load the generative model from Gemini (Gemini 1.5 Pro version)
model = genai.GenerativeModel("models/gemini-1.5-pro")

# Create a Flask Blueprint for Tool5
# - `tool5_bp` is the name of the blueprint
# - URL prefix means all routes start with /tool5
# - Template folder is "templates" where HTML files are located
tool5_bp = Blueprint("tool5_bp", __name__, url_prefix="/tool5", template_folder="templates")

# Function to extract structured data from resume text using Gemini
def resumes_details(resume):
    # Define the AI prompt for Gemini to parse the resume text
    prompt = f"""
    You are a resume parsing assistant. Given the following resume text, extract all the important details and return them in a valid JSON format.

    The resume text:
    {resume}

    Extract and include the following fields:
    {{
        "Full Name": "",
        "Contact Number": "",
        "Email Address": "",
        "Location": "",
        "Skills": {{
            "Technical Skills": [],
            "Non-Technical Skills": []
        }},
        "Education": [],
        "Work Experience": [],
        "Certifications": [],
        "Languages spoken": [],
        "Suggested Resume Category": "",
        "Recommended Job Roles": []
    }}

    Return only the JSON object with no additional text.
    """

    # Ask Gemini to generate a response based on the prompt
    response = model.generate_content(prompt).text

    # Use regex to extract just the JSON from the generated text
    json_match = re.search(r"\{.*\}", response, re.DOTALL)
    if json_match:
        response_clean = json_match.group(0)  # Extract clean JSON
    else:
        # If JSON is not found in the response, return an error
        return jsonify({"error": "Invalid JSON response from AI."})
    
    return response_clean  # Return cleaned JSON string

# Route for the index page of Tool5
@tool5_bp.route('/')
def index():
    return render_template('image.html')  # Load the HTML template for UI

# Route to handle resume upload and parsing
@tool5_bp.route('/upload_resume', methods=['POST'])
def upload_resume():
    # Check if 'resume' file field exists in the form data
    if 'resume' not in request.files:
        return jsonify({"error": "No file part"})

    file = request.files['resume']  # Get the uploaded file

    # Check if filename is empty (no file selected)
    if file.filename == '':
        return jsonify({"error": "No selected file"})

    # Proceed only if it's a valid PDF file
    if file and file.filename.endswith('.pdf'):
        text = ""  # Initialize variable to store extracted text

        # Use PyPDF2 to read the uploaded PDF
        reader = PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() or ""  # Extract text from each page

        # Send extracted text to Gemini to get structured resume details
        response = resumes_details(text)
        print("Raw Model Response:\n", response)  # Debug: show raw JSON text

        try:
            data = json.loads(response)  # Parse JSON string to Python dictionary
        except json.JSONDecodeError as e:
            # If JSON decoding fails, return an error response
            print("Error decoding JSON:", e)
            return jsonify({"error": "Failed to parse resume details. Ensure resume format is readable."})

        # Create a dictionary of extracted data with fallbacks if missing
        extracted_data = {
            "full_name": data.get("Full Name", "No Data"),
            "contact_number": data.get("Contact Number", "No Data"),
            "email_address": data.get("Email Address", "No Data"),
            "location": data.get("Location", "No Data"),
            "technical_skills": ", ".join(data.get("Skills", {}).get("Technical Skills", [])) or "No Data",
            "non_technical_skills": ", ".join(data.get("Skills", {}).get("Non-Technical Skills", [])) or "No Data",
            "education": "\n".join([
                f"{edu.get('Degree', 'N/A')} from {edu.get('Institution', 'N/A')} (Graduated: {edu.get('Years', 'N/A')})"
                for edu in data.get("Education", [])
            ]) or "No Data",
            "work_experience": "\n".join([
                f"{job.get('Job Title', 'N/A')} at {job.get('Company Name', 'N/A')} ({job.get('Years of Experience', 'N/A')})\nResponsibilities: {', '.join(job.get('Responsibilities', []))}"
                for job in data.get("Work Experience", [])
            ]) or "No Data",
            "certifications": ", ".join(data.get("Certifications", [])) or "No Data",
            "languages": ", ".join(data.get("Languages spoken", [])) or "No Data",
            "suggested_resume_category": data.get("Suggested Resume Category", "No Data"),
            "recommended_job_roles": ", ".join(data.get("Recommended Job Roles", [])) or "No Data"
        }

        # Debug print of final extracted resume data
        print("Extracted Resume Data:")
        print(json.dumps(extracted_data, indent=4))

        # Render the HTML template with extracted resume data
        return render_template('image.html', **extracted_data)

    # If the uploaded file is not a PDF
    return jsonify({"error": "Invalid file format. Please upload a PDF."})
