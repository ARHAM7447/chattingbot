from flask import Blueprint, render_template, request
from langdetect import detect
from googletrans import Translator, LANGUAGES

# Create Blueprint for tool4
tool4_bp = Blueprint("tool4", __name__, url_prefix="/tool4", template_folder="templates")

def detect_and_translate(text, target_lang):
    # Detect language
    result_lang = detect(text)

    # Translate language
    translator = Translator()
    translate_text = translator.translate(text, dest=target_lang).text

    return result_lang, translate_text

@tool4_bp.route('/')
def index():
    return render_template('tool4.html', languages=LANGUAGES)

@tool4_bp.route('/trans', methods=['POST'])
def trans():
    translation = ""
    detected_lang = ""
    if request.method == 'POST':
        text = request.form['text']
        target_lang = request.form['target_lang']
        detected_lang, translation = detect_and_translate(text, target_lang)

    return render_template('tool4.html', translation=translation, detected_lang=detected_lang, languages=LANGUAGES)