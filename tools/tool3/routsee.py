# Import required modules and packages
from flask import Blueprint, Flask, render_template, request, send_file  # Flask components for app and routing
import os  # OS module for file and directory handling
import pdfplumber  # For reading text from PDF files
import docx  # For reading text from DOCX files
from werkzeug.utils import secure_filename  # For safely handling file uploads
import google.generativeai as genai  # Google's Generative AI for content generation
from fpdf import FPDF  # To create PDF files
from dotenv import load_dotenv  # To load environment variables from a .env file

# Load environment variables (like API keys) from a .env file
load_dotenv()

# Configure the Generative AI with your API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Load the Gemini model (version 1.5 Pro)
model = genai.GenerativeModel("models/gemini-1.5-flash")

# Create a Blueprint for tool3 with a specific URL and template folder
tool3_bp = Blueprint("tool3", __name__, url_prefix="/tool3", template_folder="templates")

# Create a Flask app instance
app = Flask(__name__)

# Set directories for uploaded files and generated result files
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['RESULTS_FOLDER'] = 'results/'

# Define allowed file extensions for uploads
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'txt', 'docx'}

# Create the necessary folders if they don't already exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)

# Function to check if uploaded file has a valid extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Function to extract text from PDF, DOCX, or TXT files
def extract_text_from_file(file_path):
    ext = file_path.rsplit('.', 1)[1].lower()  # Get file extension
    if ext == 'pdf':
        with pdfplumber.open(file_path) as pdf:
            # Combine text from all PDF pages
            text = ''.join([page.extract_text() or '' for page in pdf.pages])
        return text
    elif ext == 'docx':
        # Read paragraphs from the DOCX file
        doc = docx.Document(file_path)
        return ' '.join([para.text for para in doc.paragraphs])
    elif ext == 'txt':
        # Read all content from a TXT file
        with open(file_path, 'r', encoding="utf-8") as file:
            return file.read()
    return None  # If format not supported

# Function to generate MCQs from input text using Gemini AI model
def generate_mcqs_from_text(input_text, num_questions):
    # Prompt to guide the AI on how to generate MCQs
    prompt = f"""
    You are an AI assistant helping the user generate multiple-choice questions (MCQs) based on the following text:
    '{input_text}'
    Please generate {num_questions} MCQs from the text. Each question should have:
    - A clear question
    - Four answer options (labeled A, B, C, D)
    - The correct answer clearly indicated
    Format:
    ## MCQ
    Question: [question]
    A) [option A]
    B) [option B]
    C) [option C]
    D) [option D]
    Correct Answer: [correct option]
    """
    # Call Gemini model to generate response
    response = model.generate_content(prompt).text.strip()
    return response

# Save the generated MCQs to a .txt file
def save_mcqs_to_file(mcqs, filename):
    results_path = os.path.join(app.config['RESULTS_FOLDER'], filename)
    with open(results_path, 'w', encoding="utf-8") as f:
        f.write(mcqs)
    return results_path

# Create a PDF file with the generated MCQs
def create_pdf(mcqs, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Split and add each MCQ to the PDF
    for mcq in mcqs.split("## MCQ"):
        if mcq.strip():
            pdf.multi_cell(0, 10, mcq.strip())  # Write MCQ content
            pdf.ln(5)  # Add space between questions

    pdf_path = os.path.join(app.config['RESULTS_FOLDER'], filename)
    pdf.output(pdf_path)
    return pdf_path

# Route to render the initial upload form page
@tool3_bp.route('/')
def index():
    return render_template('mcqs.html')  # Show form to upload file and select number of questions

# Route to handle form submission and generate MCQs
@tool3_bp.route('/generate', methods=['POST'])
def generate_mcqs():
    if 'file' not in request.files:
        return "No file uploaded"  # If file not found in form

    file = request.files['file']  # Get the uploaded file
    if file and allowed_file(file.filename):  # Validate file extension
        filename = secure_filename(file.filename)  # Secure the filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)  # Set save path
        file.save(file_path)  # Save uploaded file

        # Extract text from uploaded file
        text = extract_text_from_file(file_path)
        if text:
            try:
                # Get number of questions from form input
                num_questions = int(request.form['num_questions'])

                # Generate MCQs from extracted text
                mcqs = generate_mcqs_from_text(text, num_questions)

                # Save MCQs in text and PDF formats
                txt_filename = f"generated_mcqs_{filename.rsplit('.', 1)[0]}.txt"
                pdf_filename = f"generated_mcqs_{filename.rsplit('.', 1)[0]}.pdf"
                save_mcqs_to_file(mcqs, txt_filename)
                create_pdf(mcqs, pdf_filename)

                # Render results page with generated MCQs and download links
                return render_template('results.html', mcqs=mcqs, txt_filename=txt_filename, pdf_filename=pdf_filename)
            except Exception as e:
                return f"Error generating MCQs: {str(e)}"  # Handle any generation errors
    return "Invalid file format"  # If file type not supported

# Route to handle file download (PDF or TXT)
@tool3_bp.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['RESULTS_FOLDER'], filename)
    return send_file(file_path, as_attachment=True)  # Send file as downloadable attachment
