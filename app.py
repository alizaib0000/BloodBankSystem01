from flask import Flask, request, redirect, render_template, session, url_for, flash, jsonify
import pymysql
from flask_mail import Message, Mail
import os

# Flask App Initialization
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "22852255")  # Store in environment for security

# Flask-Mail Configuration (Make sure to use environment variables)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'your_email@gmail.com')  # Environment variable
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'your_password')  # Environment variable
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'your_email@gmail.com')  # Sender email
mail = Mail(app)

# MySQL Database Connection (Create a connection for each request)
def get_db_connection():
    return pymysql.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", "22852255"),
        database=os.environ.get("DB_NAME", "blood_bank_system")
    )

# Routes and Functions
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/about')
def about():
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM donations")
    total_donations = cursor.fetchone()[0]
    cursor.execute("SELECT blood_type, COUNT(*) FROM donations GROUP BY blood_type")
    donation_stats = cursor.fetchall()
    db.close()
    return render_template('about.html', total_donations=total_donations, donation_stats=donation_stats)

@app.route('/contact')
def contact():
    return render_template('contact.html')

# Other routes go here, following the same pattern

@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out successfully.", "success")
    return redirect(url_for('login'))

# debug on host or port 80
port = int(os.environ.get('PORT', 8000))
app.run(host='0.0.0.0', port=port)
