from flask import Flask, render_template, request, redirect, url_for, flash
from tools.tool1.routes import tool1_bp
from tools.tool2.routes1 import tool2_bp
from tools.tool3.routsee import tool3_bp
from tools.tool4.routing import tool4_bp
from tools.tool5.image import tool5_bp
from tools.tool6.tool import tool6_bp
from tools.tool7.scam import tool7_bp
from cognito_helper import signup_user, login_user, confirm_user
import requests
import logging
import os

app = Flask(__name__, template_folder='templates')
app.secret_key = 'your_secret_key_here'  # Change this!

# API Gateway Endpoint
API_GATEWAY_URL = 'https://2kznmnga9e.execute-api.ap-southeast-2.amazonaws.com/feedback'

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Register Blueprints
app.register_blueprint(tool1_bp, url_prefix='/tool1')
app.register_blueprint(tool2_bp, url_prefix='/tool2')
app.register_blueprint(tool3_bp, url_prefix='/tool3')
app.register_blueprint(tool4_bp, url_prefix='/tool4')
app.register_blueprint(tool5_bp, url_prefix='/tool5')
app.register_blueprint(tool6_bp, url_prefix='/tool6')
app.register_blueprint(tool7_bp, url_prefix='/tool7')

# Routes
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/ai')
def ai():
    return render_template('ai.html')

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            message = request.form.get('message', '').strip()

            # Validate inputs
            if not name or not email or not message:
                flash('All fields are required.', 'warning')
                return redirect(url_for('feedback'))

            payload = {
                'name': name,
                'email': email,
                'message': message
            }

            logging.debug(f"Payload to be sent: {payload}")

            # Call your Lambda endpoint
            API_GATEWAY_URL = 'https://2kznmnga9e.execute-api.ap-southeast-2.amazonaws.com/feedback'   # Replace this with your real URL
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.post(API_GATEWAY_URL, json=payload, headers=headers, timeout=10)

            logging.debug(f"Lambda response code: {response.status_code}")
            logging.debug(f"Lambda response body: {response.text}")

            if response.status_code == 200:
                flash('Thanks for your feedback!', 'success')
            else:
                flash('Failed to send feedback. Please try again later.', 'danger')

        except requests.exceptions.Timeout:
            flash('Request timed out. Please try again later.', 'danger')
            logging.error("Request timed out.")

        except requests.exceptions.ConnectionError:
            flash('Connection error. Check your internet or Lambda URL.', 'danger')
            logging.error("Connection error.")

        except Exception as e:
            logging.exception("An unexpected error occurred.")
            flash('Something went wrong while sending feedback.', 'danger')

        return redirect(url_for('feedback'))

    return render_template('feedback.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        result = signup_user(email, password)

        if result.get('success'):
            flash("📧 Signup successful! Check your email for the confirmation code.", "info")
            return redirect(url_for('confirm'))
        else:
            flash(f"❌ Signup failed: {result.get('message')}", "danger")

    return render_template('signup.html')

@app.route('/confirm', methods=['GET', 'POST'])
def confirm():
    if request.method == 'POST':
        email = request.form.get('email')
        code = request.form.get('code')

        result = confirm_user(email, code)

        if result.get('success'):
            flash("✅ Account confirmed! You can now log in.", "success")
            return redirect(url_for('login'))
        else:
            flash(f"❌ Confirmation failed: {result.get('message')}", "danger")

    return render_template('confirm.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        result = login_user(email, password)

        if result.get('success'):
            flash("🎉 Login successful!", "success")
            return redirect(url_for('index'))
        else:
            flash(f"❌ Login failed: {result.get('message')}", "danger")

    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
