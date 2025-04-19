from flask import Flask, render_template, request, redirect, url_for, flash
# Importing necessary modules from Flask

from tools.tool1.routes import tool1_bp
from tools.tool2.routes1 import tool2_bp
from tools.tool3.routsee import tool3_bp
from tools.tool4.routing import tool4_bp
from tools.tool5.image import tool5_bp
from tools.tool6.tool import tool6_bp
from tools.tool7.scam import tool7_bp
# Importing blueprints from different tool modules

from cognito_helper import signup_user, login_user, confirm_user
# Importing functions for user authentication with AWS Cognito

import requests
# For sending HTTP requests

import logging
# For logging debug and error messages

import os
# To interact with the operating system environment

from dotenv import load_dotenv
# To load environment variables from a .env file

load_dotenv()  
# Load all the environment variables from the .env file

app = Flask(__name__, template_folder='templates')
# Creating the Flask application and setting the templates folder

app.secret_key = 'your_secret_key_here'  # Change this!
# Setting a secret key used for securely signing the session cookies

# API Gateway Endpoint
API_GATEWAY_URL = 'https://2kznmnga9e.execute-api.ap-southeast-2.amazonaws.com/feedback'
# Storing the API Gateway endpoint URL to send feedback to a Lambda function

# Setup logging
logging.basicConfig(level=logging.DEBUG)
# Configuring logging level to DEBUG for detailed logs

# Register Blueprints
app.register_blueprint(tool1_bp, url_prefix='/tool1')
app.register_blueprint(tool2_bp, url_prefix='/tool2')
app.register_blueprint(tool3_bp, url_prefix='/tool3')
app.register_blueprint(tool4_bp, url_prefix='/tool4')
app.register_blueprint(tool5_bp, url_prefix='/tool5')
app.register_blueprint(tool6_bp, url_prefix='/tool6')
app.register_blueprint(tool7_bp, url_prefix='/tool7')
# Registering all the tool blueprints with their respective URL prefixes

# Routes
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')
# Homepage route that renders the index.html template

@app.route('/about')
def about():
    return render_template('about.html')
# About page route that renders about.html

@app.route('/ai')
def ai():
    return render_template('ai.html')
# AI tools page route that renders ai.html

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            message = request.form.get('message', '').strip()
            # Getting and cleaning the form data from the feedback form

            # Validate inputs
            if not name or not email or not message:
                flash('All fields are required.', 'warning')
                return redirect(url_for('feedback'))
            # Checking if all fields are filled. If not, show a warning and redirect.

            payload = {
                'name': name,
                'email': email,
                'message': message
            }
            # Creating a dictionary (payload) to send to the API

            logging.debug(f"Payload to be sent: {payload}")
            # Logging the payload for debugging

            # Call your Lambda endpoint
            API_GATEWAY_URL = 'https://2kznmnga9e.execute-api.ap-southeast-2.amazonaws.com/feedback'   # Replace this with your real URL
            headers = {
                'Content-Type': 'application/json'
            }
            # Preparing headers for the HTTP POST request

            response = requests.post(API_GATEWAY_URL, json=payload, headers=headers, timeout=10)
            # Sending POST request to the API Gateway URL with the feedback data

            logging.debug(f"Lambda response code: {response.status_code}")
            logging.debug(f"Lambda response body: {response.text}")
            # Logging the API response for debugging

            if response.status_code == 200:
                flash('Thanks for your feedback!', 'success')
                # Show success message if feedback was successfully sent
            else:
                flash('Failed to send feedback. Please try again later.', 'danger')
                # Show error message if response code is not 200

        except requests.exceptions.Timeout:
            flash('Request timed out. Please try again later.', 'danger')
            logging.error("Request timed out.")
            # Handle timeout exception

        except requests.exceptions.ConnectionError:
            flash('Connection error. Check your internet or Lambda URL.', 'danger')
            logging.error("Connection error.")
            # Handle connection error exception

        except Exception as e:
            logging.exception("An unexpected error occurred.")
            flash('Something went wrong while sending feedback.', 'danger')
            # Catch-all for any other exception and log it

        return redirect(url_for('feedback'))
        # Redirect back to the feedback page after handling POST

    return render_template('feedback.html')
    # Render feedback form if request is GET

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        # Getting email and password from the signup form

        result = signup_user(email, password)
        # Calling Cognito helper function to sign up the user

        if result.get('success'):
            flash("📧 Signup successful! Check your email for the confirmation code.", "info")
            return redirect(url_for('confirm'))
            # If successful, redirect user to the confirm page
        else:
            flash(f"❌ Signup failed: {result.get('message')}", "danger")
            # Show error message if signup fails

    return render_template('signup.html')
    # Render the signup page for GET request

@app.route('/confirm', methods=['GET', 'POST'])
def confirm():
    if request.method == 'POST':
        email = request.form.get('email')
        code = request.form.get('code')
        # Getting email and confirmation code from form

        result = confirm_user(email, code)
        # Calling Cognito helper to confirm the user

        if result.get('success'):
            flash("✅ Account confirmed! You can now log in.", "success")
            return redirect(url_for('login'))
            # On successful confirmation, redirect to login page
        else:
            flash(f"❌ Confirmation failed: {result.get('message')}", "danger")
            # Show error if confirmation fails

    return render_template('confirm.html')
    # Render confirm page on GET request

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        # Getting login credentials from the form

        result = login_user(email, password)
        # Calling Cognito helper function to log in the user

        if result.get('success'):
            flash("🎉 Login successful!", "success")
            return redirect(url_for('index'))
            # If login is successful, redirect to homepage
        else:
            flash(f"❌ Login failed: {result.get('message')}", "danger")
            # Show error message if login fails

    return render_template('login.html')
    # Render the login form on GET request

if __name__ == '__main__':
    app.run(debug=True)
# This line runs the Flask development server in debug mode if the script is executed directly
