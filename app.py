from flask import Flask, render_template, request, redirect, url_for, flash
from tools.tool1.routes import tool1_bp
from tools.tool2.routes1 import tool2_bp
from tools.tool3.routsee import tool3_bp
from tools.tool4.routing import tool4_bp
from tools.tool5.image import tool5_bp
from tools.tool6.tool import tool6_bp
from tools.tool7.scam import tool7_bp
from cognito_helper import signup_user, login_user, confirm_user
import os

app = Flask(__name__, template_folder='templates')
app.secret_key = 'your_secret_key_here'  # Required for flash messages

# ✅ Register Blueprints
app.register_blueprint(tool1_bp, url_prefix='/tool1')
app.register_blueprint(tool2_bp, url_prefix='/tool2')
app.register_blueprint(tool3_bp, url_prefix='/tool3')
app.register_blueprint(tool4_bp, url_prefix='/tool4')
app.register_blueprint(tool5_bp, url_prefix='/tool5')
app.register_blueprint(tool6_bp, url_prefix='/tool6')
app.register_blueprint(tool7_bp, url_prefix='/tool7')

# ✅ Main Routes
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
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        print(f"💬 Feedback received from {name} ({email}): {message}")
        return render_template('feedback.html', success=True)
    return render_template('feedback.html', success=False)


# ✅ Cognito Signup Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        print("📨 Received signup form submission")
        print(f"Email: {email}, Password: {'*' * len(password)}")

        result = signup_user(email, password)
        print("📊 Result from Cognito signup_user():", result)

        if result.get('success'):
            flash("📧 Signup successful! Please check your email for the confirmation code.", "info")
            return redirect(url_for('confirm'))  # ✅ send user to confirm page
        else:
            flash(result.get('error', 'Signup failed.'), 'danger')
            print("❌ Signup failed with error:", result.get('error'))

    return render_template('signup.html')


# ✅ Cognito Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        print("🔑 Received login form submission")
        print(f"Email: {email}, Password: {'*' * len(password)}")

        result = login_user(email, password)
        print("📊 Result from Cognito login_user():", result)

        if result.get('success'):
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash(result.get('error', 'Login failed.'), 'danger')
            print("❌ Login failed with error:", result.get('error'))

    return render_template('login.html')

@app.route('/confirm', methods=['GET', 'POST'])
def confirm():
    if request.method == 'POST':
        email = request.form.get('email')
        code = request.form.get('code')

        result = confirm_user(email, code)
        print("📊 Result from Cognito confirm_user():", result)

        if result.get('success'):
            flash("✅ Account confirmed successfully! You can now log in.", "success")
            return redirect(url_for('login'))
        else:
            flash(result.get('error', 'Confirmation failed.'), 'danger')

    return render_template('confirm.html')


# ✅ Run Flask App
if __name__ == '__main__':
    app.run(debug=True)
