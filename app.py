from flask import Flask, render_template
from tools.tool1.routes import tool1_bp
app = Flask(__name__, template_folder='templates')

# Register Blueprints for all AI tools
app.register_blueprint(tool1_bp, template_folder='tools/tool1/templates')

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/feedback')
def feedback():  # This is fine, the feedback function handles /feedback
    return render_template('feedback.html')

@app.route('/ai')
def ai():  # Renamed the function to "ai" for uniqueness
    return render_template('ai.html')

if __name__ == '__main__':
    app.run(debug=True)
