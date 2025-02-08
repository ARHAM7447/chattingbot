from flask import Flask, render_template

app = Flask(__name__)

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
