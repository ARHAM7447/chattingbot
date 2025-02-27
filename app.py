from flask import Flask, render_template, request, redirect, url_for
from tools.tool1.routes import tool1_bp  # Import tool1 blueprint
from tools.tool2.routes1 import tool2_bp  # Import tool2 blueprint
from tools.tool3.routsee import tool3_bp
from tools.tool4.routing import tool4_bp  # Import tool4 blueprint
from tools.tool5.image import tool5_bp  # Import tool5 blueprint
import os

app = Flask(__name__, template_folder='templates')

# Register Blueprints with URL prefixes for better organization
app.register_blueprint(tool1_bp, url_prefix='/tool1')
app.register_blueprint(tool2_bp, url_prefix='/tool2')
app.register_blueprint(tool3_bp, url_prefix='/tool3')
app.register_blueprint(tool4_bp, url_prefix='/tool4')
app.register_blueprint(tool5_bp, url_prefix='/tool5')

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
        
        # Here you can add code to handle the feedback, e.g., save it to a file or database
        # For now, we'll just print it to the console
        print(f"Feedback received: {name}, {email}, {message}")
        
        return redirect(url_for('feedback'))
    return render_template('feedback.html')

@app.route('/ai')
def ai():
    return render_template('ai.html')

if __name__ == '__main__':
    app.run(debug=True)