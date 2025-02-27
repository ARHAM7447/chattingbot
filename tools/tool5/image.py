from flask import Blueprint, render_template, request, jsonify
from PyPDF2 import PdfReader
import google.generativeai as genai
import os
import json
import re

# Set your API key
os.environ["GOOGLE_API_KEY"] = "AIzaSyCS_vlMLsisM9_VbzflZzkzgBEbqc4tzyg"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# Load model
model = genai.GenerativeModel("models/gemini-1.5-pro")

# Create Blueprint for Tool5
tool5_bp = Blueprint("tool5_bp", __name__, url_prefix="/tool5", template_folder="templates")

def resumes_details(resume):
    # Prompt with detailed request
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

    # Generate response from the model
    response = model.generate_content(prompt).text
    
    # Extract valid JSON using regex
    json_match = re.search(r"\{.*\}", response, re.DOTALL)
    if json_match:
        response_clean = json_match.group(0)
    else:
        return jsonify({"error": "Invalid JSON response from AI."})
    
    return response_clean

@tool5_bp.route('/')
def index():
    return render_template('image.html')

@tool5_bp.route('/upload_resume', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({"error": "No file part"})

    file = request.files['resume']
    if file.filename == '':
        return jsonify({"error": "No selected file"})

    if file and file.filename.endswith('.pdf'):
        # Extract text from the PDF
        text = ""
        reader = PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() or ""

        # Get resume details from the model
        response = resumes_details(text)
        print("Raw Model Response:\n", response)

        # Load the cleaned response into a dictionary
        try:
            data = json.loads(response)
        except json.JSONDecodeError as e:
            print("Error decoding JSON:", e)
            return jsonify({"error": "Failed to parse resume details. Ensure resume format is readable."})

        # Extract details from the JSON response
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

        # Debugging statements
        print("Extracted Resume Data:")
        print(json.dumps(extracted_data, indent=4))

        # Render the template and pass extracted values
        return render_template('image.html', **extracted_data)

    return jsonify({"error": "Invalid file format. Please upload a PDF."})
