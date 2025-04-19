# Import necessary modules from Flask and other libraries
from flask import Blueprint, render_template, request  # For creating routes and handling web requests
from langdetect import detect  # To detect the language of the input text
from googletrans import Translator, LANGUAGES  # Translator for translation and list of supported languages

# Create a Flask Blueprint for Tool 4 with a specific URL prefix and template folder
tool4_bp = Blueprint("tool4", __name__, url_prefix="/tool4", template_folder="templates")

# Function to detect language and translate text
def detect_and_translate(text, target_lang):
    # Detect the original language of the input text
    result_lang = detect(text)

    # Create a translator instance
    translator = Translator()

    # Translate the input text to the selected target language
    translate_text = translator.translate(text, dest=target_lang).text

    # Return both detected language and translated text
    return result_lang, translate_text

# Route to display the translation form page
@tool4_bp.route('/')
def index():
    # Render the tool4.html template and pass all available language codes and names
    return render_template('tool4.html', languages=LANGUAGES)

# Route to handle translation when form is submitted
@tool4_bp.route('/trans', methods=['POST'])
def trans():
    # Initialize translation and detected_lang variables as empty strings
    translation = ""
    detected_lang = ""

    # Check if the method is POST (form submission)
    if request.method == 'POST':
        # Get the input text from the form
        text = request.form['text']

        # Get the selected target language from the form
        target_lang = request.form['target_lang']

        # Call the detect_and_translate function to get detected language and translated result
        detected_lang, translation = detect_and_translate(text, target_lang)

    # Render the template again and pass translation result, detected language, and languages list
    return render_template('tool4.html', translation=translation, detected_lang=detected_lang, languages=LANGUAGES)
