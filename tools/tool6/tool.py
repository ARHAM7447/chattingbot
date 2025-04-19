# Import required modules from Flask and other libraries
from flask import Flask, Blueprint, render_template, request  # Flask core modules
import spacy  # spaCy for natural language processing (NLP)
from spacy import displacy  # For rendering named entities visually in HTML
import fitz  # PyMuPDF for reading PDF files

# Initialize the main Flask app
app = Flask(__name__)

# Create a Blueprint for Tool6
# - `tool6_bp` is the name of the blueprint
# - `__name__` tells Flask where to find resources
# - `url_prefix="/tool6"` means all routes will start with /tool6
# - `template_folder="templates"` tells Flask where to find HTML templates
tool6_bp = Blueprint("tool6_bp", __name__, url_prefix="/tool6", template_folder="templates")

# Load the small English language model from spaCy
nlp = spacy.load("en_core_web_sm")

# Route for the main tool6 page (GET request)
@tool6_bp.route('/')
def index():
    # Render the initial form page (entitiy.html)
    return render_template('entitiy.html')

# Route to handle the entity extraction logic (POST for form submission, GET fallback)
@tool6_bp.route('/entity', methods=['POST', 'GET'])
def entity():
    # Check if the request method is POST (form submitted)
    if request.method == 'POST':
        file = request.files.get('file')  # Get uploaded file from form

        # If a file was uploaded
        if file:
            text = ""  # Initialize variable to store extracted text

            # If the uploaded file is a PDF
            if file.filename.endswith('.pdf'):
                # Read the PDF using PyMuPDF from file stream
                pdf_document = fitz.open(stream=file.read(), filetype="pdf")
                # Loop through each page and extract text
                for page in pdf_document:
                    text += page.get_text("text")  # Extract plain text from page
                pdf_document.close()  # Close the PDF file
            else:
                # Handle plain text files by decoding bytes to string
                text = file.read().decode('utf-8', errors='ignore')

            # Process the extracted text using spaCy's NLP pipeline
            doc = nlp(text)
            # Render the named entities in HTML using spaCy's displacy tool
            html = displacy.render(doc, style='ent', page=True)  # `page=True` returns full HTML page

            # Pass the HTML and original text back to the template
            return render_template('entitiy.html', html=html, text=text)

    # If GET request or no file, just render the empty page
    return render_template('entitiy.html')

# Register the blueprint with the main Flask app
app.register_blueprint(tool6_bp)

# Run the Flask app in debug mode (auto-reloads on code changes)
if __name__ == '__main__':
    app.run(debug=True)
