from flask import Flask, request, redirect, render_template, session, url_for, flash, jsonify
import pymysql
from flask_mail import Message, Mail
import os

# Flask App Initialization
app = Flask(__name__)

# Environment Variables for Koyeb
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "22852255")  # Use Koyeb environment variable

# MySQL Database Connection using environment variables
db = pymysql.connect(
    host=os.environ.get("DB_HOST", "localhost"),  # Database host
    user=os.environ.get("DB_USER", "root"),  # MySQL username
    password=os.environ.get("DB_PASSWORD", "22852255"),  # MySQL password
    database=os.environ.get("DB_NAME", "blood_bank_system")  # Database name
)

cursor = db.cursor()

# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'bloodbanksystem018@gmail.com')  # Replace with your email
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'mthk qeas wvua eomo')  # App password or Gmail password
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'bloodbanksystem018@gmail.com')  # Sender email
mail = Mail(app)

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/features')
def features():
   return render_template('features.html')

@app.route('/about')
def about():
    cursor.execute("SELECT COUNT(*) FROM donations")
    total_donations = cursor.fetchone()[0]

    cursor.execute("SELECT blood_type, COUNT(*) FROM donations GROUP BY blood_type")
    donation_stats = cursor.fetchall()
    
    return render_template('about.html', total_donations=total_donations, donation_stats=donation_stats)

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/needblood', methods=['GET', 'POST'])
def need_blood():
    if request.method == 'POST':
        patient_name = request.form['patient_name']
        blood_group = request.form['blood_group']
        contact_number = request.form['contact_number']
        required_date = request.form['required_date']
        location = request.form['location']
        additional_info = request.form.get('additional_info', '')

        if not patient_name or not blood_group or not contact_number or not required_date or not location:
            flash('Please fill in all the required fields.', 'error')
            return redirect('/needblood')

        try:
            query = """
            INSERT INTO need_blood (patient_name, blood_group, contact_number, required_date, location, additional_info)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (patient_name, blood_group, contact_number, required_date, location, additional_info))
            db.commit()

            flash('Your blood request has been successfully submitted!', 'success')
            return redirect('/needblood')
        except pymysql.MySQLError as e:
            flash(f'Error inserting data: {e}', 'error')
            return redirect('/needblood')

    return render_template('needblood.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']

        query = "INSERT INTO users (name, email, phone, password) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (name, email, phone, password))
        db.commit() 
        
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        query = "SELECT id, name, password FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()

        if user and user[2] == password:
            session['user_id'] = user[0]
            session['username'] = user[1]
            
            flash("Login successfully!")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials, please try again.", "error")

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        username = session.get('username')
        return render_template('dashboard.html', username=username)
    else:
        return redirect(url_for('login'))

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

if __name__ == "__main__":
    # Make sure to run with the correct port for Koyeb environment
    port = int(os.environ.get("PORT", 8000))  # Get PORT from environment or default to 8000
    app.run(host="0.0.0.0", port=port, debug=True)  # Enable debug for easier troubleshooting during development

