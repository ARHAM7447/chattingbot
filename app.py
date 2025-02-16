from flask import Flask, render_template
from tools.tool1.routes import tool1_bp  # Import tool1 blueprint
from tools.tool2.routes1 import tool2_bp  # Import tool2 blueprint
from tools.tool3.routsee import tool3_bp
from tools.tool4.routing import tool4_bp  # Import tool4 blueprint
app = Flask(__name__, template_folder='templates')

# Register Blueprints for all AI tools
app.register_blueprint(tool1_bp, url_prefix='/tool1')  # Use url_prefix for clarity
app.register_blueprint(tool2_bp, url_prefix='/tool2')  # Register tool2 properly
app.register_blueprint(tool3_bp, url_prefix='/tool3')  # Register tool3 properly
app.register_blueprint(tool4_bp, url_prefix='/tool4')  # Register tool4 properly


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/feedback')
def feedback():
    return render_template('feedback.html')

@app.route('/ai')
def ai():
    return render_template('ai.html')

if __name__ == '__main__':
    app.run(debug=True)
