from flask import Flask, Blueprint, render_template, request
import spacy
from spacy import displacy
import fitz  # PyMuPDF

# Initialize Flask app
app = Flask(__name__)

# Create Blueprint for Tool6
tool6_bp = Blueprint("tool6_bp", __name__, url_prefix="/tool6", template_folder="templates")

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

@tool6_bp.route('/')
def index():
    return render_template('entitiy.html')

@tool6_bp.route('/entity', methods=['POST', 'GET'])
def entity():
    if request.method == 'POST':
        file = request.files.get('file')

        if file:
            text = ""

            # Check if the file is a PDF
            if file.filename.endswith('.pdf'):
                pdf_document = fitz.open(stream=file.read(), filetype="pdf")
                for page in pdf_document:
                    text += page.get_text("text")  # Extract text from PDF pages
                pdf_document.close()
            else:
                # Handle text files (UTF-8 decoding)
                text = file.read().decode('utf-8', errors='ignore')

            # Process text using spaCy
            doc = nlp(text)
            html = displacy.render(doc, style='ent', page=True)  # `page=True` ensures proper HTML rendering

            return render_template('entitiy.html', html=html, text=text)

    return render_template('entitiy.html')

# Register Blueprint
app.register_blueprint(tool6_bp)

if __name__ == '__main__':
    app.run(debug=True)
