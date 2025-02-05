from flask import Flask, request, redirect, render_template, session, url_for, flash
import pymysql
from flask_mail import Mail, Message
import os

# Flask App Initialization
app = Flask(__name__)
app.secret_key = '22852255'  # Change this for security

# Koyeb MySQL Configuration
db_config = {
    "host": "ep-bitter-meadow-a28wptyo.eu-central-1.pg.koyeb.app",  # Koyeb MySQL Host
    "user": "koyeb-adm",  # Koyeb MySQL Username
    "password": "npg_xKniF8EDCt2A",  # Koyeb MySQL Password
    "database": "blood_bank_system",  # Your MySQL Database Name
    "port": 3306  # Default MySQL Port
}

# Function to connect to MySQL database
def get_db_connection():
    try:
        connection = pymysql.connect(
            host=db_config["host"],
            user=db_config["user"],
            password=db_config["password"],
            database=db_config["database"],
            port=db_config["port"],
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except pymysql.MySQLError as e:
        print(f"Database connection error: {e}")
        return None

# Flask-Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'bloodbanksystem018@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'mthk qeas wvua eomo'  # Use App Password
app.config['MAIL_DEFAULT_SENDER'] = 'bloodbanksystem018@gmail.com'
mail = Mail(app)

# Home Route
@app.route('/index')
def home():
    return render_template('index.html')

# Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']

        try:
            db = get_db_connection()
            if db is None:
                flash("Database connection failed!", "error")
                return redirect('/register')

            cursor = db.cursor()
            query = "INSERT INTO users (name, email, phone, password) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (name, email, phone, password))
            db.commit()

            flash("Registration successful! Please log in.", "success")
        except pymysql.MySQLError as e:
            flash(f"Database error: {e}", "error")
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()

        return redirect(url_for('login'))
    
    return render_template('register.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        db = get_db_connection()
        if db is None:
            flash("Database connection failed!", "error")
            return redirect('/login')

        cursor = db.cursor()
        query = "SELECT id, name, password FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()
        cursor.close()
        db.close()

        if user and user['password'] == password:
            session['user_id'] = user['id']
            session['username'] = user['name']
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials, please try again.", "error")

    return render_template('login.html')

# Dashboard Route
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session.get('username'))

# Logout Route
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for('login'))

# Need Blood Request Route
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
            flash('Please fill in all required fields.', 'error')
            return redirect('/needblood')

        try:
            db = get_db_connection()
            if db is None:
                flash("Database connection failed!", "error")
                return redirect('/needblood')

            cursor = db.cursor()
            query = """
            INSERT INTO need_blood (patient_name, blood_group, contact_number, required_date, location, additional_info)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (patient_name, blood_group, contact_number, required_date, location, additional_info))
            db.commit()
            flash('Blood request submitted successfully!', 'success')
        except pymysql.MySQLError as e:
            flash(f'Database error: {e}', 'error')
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()

    return render_template('needblood.html')

# Send Email Route (Example)
@app.route('/send_email')
def send_email():
    try:
        msg = Message("Test Email", recipients=["recipient@example.com"])
        msg.body = "This is a test email from Flask."
        mail.send(msg)
        return "Email sent successfully!"
    except Exception as e:
        return f"Error sending email: {e}"

# Prevent Caching
@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# Run Flask App
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
