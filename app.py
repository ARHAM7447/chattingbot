from flask import Flask, render_template, request, redirect, url_for
from tools.tool1.routes import tool1_bp  # Import tool1 blueprint
from tools.tool2.routes1 import tool2_bp  # Import tool2 blueprint
from tools.tool3.routsee import tool3_bp  # Ensure correct file name
from tools.tool4.routing import tool4_bp  # Import tool4 blueprint
from tools.tool5.image import tool5_bp  # Import tool5 blueprint
from tools.tool6.tool import tool6_bp  # Ensure correct module name
from tools.tool7.scam import tool7_bp  
import os

app = Flask(__name__, template_folder='templates')

# Register Blueprints with URL prefixes for better organization
app.register_blueprint(tool1_bp, url_prefix='/tool1')
app.register_blueprint(tool2_bp, url_prefix='/tool2')
app.register_blueprint(tool3_bp, url_prefix='/tool3')
app.register_blueprint(tool4_bp, url_prefix='/tool4')
app.register_blueprint(tool5_bp, url_prefix='/tool5')
app.register_blueprint(tool6_bp, url_prefix='/tool6')  # ✅ Fixed this line
app.register_blueprint(tool7_bp, url_prefix='/tool7')

# Define routes for rendering templates
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        
        # Handle feedback (e.g., save to a database or log file)
        print(f"Feedback received: {name}, {email}, {message}")
        
        return render_template('feedback.html', success=True)  # Show a success message
    return render_template('feedback.html', success=False)

@app.route('/ai')
def ai():
    return render_template('ai.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # TODO: Add user registration logic (e.g., save to database)
        print(f"User signed up: {username}, {email}")

        return redirect(url_for('login'))  # Redirect to login page after signup
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # TODO: Add authentication logic (e.g., check credentials from database)
        print(f"User login attempt: {email}")

        return redirect(url_for('index'))  # Redirect to homepage after login

    return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True)
