from flask import Flask, request, redirect, render_template, session, url_for, flash
import pymysql
import os
from flask_mail import Mail, Message

# Flask App Initialization
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "22852255")  # Secret key for sessions

# Database Configuration for FreeSQLDatabase
db_config = {
    "host": "sql7.freesqldatabase.com",
    "port": 3306,
    "user": "sql7761392",  # Replace with your username
    "password": "uCMiaNNZfW",  # Replace with your actual password
    "database": "sql7761392"  # Replace with your database name
}

# Flask-Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'bloodbanksystem018@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'mthk qeas wvua eomo')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'bloodbanksystem018@gmail.com')
mail = Mail(app)

# Function to get a database connection
def get_db_connection():
    try:
        connection = pymysql.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database'],
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

# Routes
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/about')
def about():
    return render_template('about.html')

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
            db = get_db_connection()
            if db is None:
                flash('Could not connect to the database.', 'error')
                return redirect('/needblood')

            cursor = db.cursor()
            query = """
            INSERT INTO need_blood (patient_name, blood_group, contact_number, required_date, location, additional_info)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (patient_name, blood_group, contact_number, required_date, location, additional_info))
            db.commit()
            flash('Your blood request has been successfully submitted!', 'success')
        except pymysql.MySQLError as e:
            flash(f'Error inserting data: {e}', 'error')
        finally:
            cursor.close()
            db.close()

    return render_template('needblood.html')

@app.route('/donateblood', methods=['GET', 'POST'])
def donate_blood():
    if request.method == 'POST':
        donor_name = request.form['donor_name']
        blood_group = request.form['blood_group']
        contact_number = request.form['contact_number']
        location = request.form['location']

        if not donor_name or not blood_group or not contact_number or not location:
            flash('Please fill in all the required fields.', 'error')
            return redirect('/donateblood')

        try:
            db = get_db_connection()
            if db is None:
                flash('Could not connect to the database.', 'error')
                return redirect('/donateblood')

            cursor = db.cursor()
            query = """
            INSERT INTO donate_blood (donor_name, blood_group, contact_number, location)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (donor_name, blood_group, contact_number, location))
            db.commit()
            flash('Your donation has been successfully registered!', 'success')

            # Sending Email after successful donation registration
            send_donation_email(donor_name, blood_group, contact_number, location)
        except pymysql.MySQLError as e:
            flash(f'Error inserting data: {e}', 'error')
        finally:
            cursor.close()
            db.close()

    return render_template('donateblood.html')

# Function to send donation email
def send_donation_email(donor_name, blood_group, contact_number, location):
    try:
        subject = "Blood Donation Registered"
        body = f"Dear {donor_name},\n\nThank you for registering as a blood donor. Here are your details:\n\nBlood Group: {blood_group}\nContact: {contact_number}\nLocation: {location}\n\nThank you for your support!"
        msg = Message(subject, recipients=["recipient@example.com"])  # Send to relevant recipients
        msg.body = body
        mail.send(msg)
        print("Donation email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")

@app.route('/searchdonor', methods=['GET', 'POST'])
def search_donor():
    donors = []
    if request.method == 'POST':
        blood_group = request.form['blood_group']
        location = request.form['location']

        try:
            db = get_db_connection()
            if db is None:
                flash('Could not connect to the database.', 'error')
                return redirect('/searchdonor')

            cursor = db.cursor()
            query = "SELECT donor_name, blood_group, contact_number, location FROM donate_blood WHERE blood_group = %s AND location = %s"
            cursor.execute(query, (blood_group, location))
            donors = cursor.fetchall()
        except pymysql.MySQLError as e:
            flash(f'Error searching for donors: {e}', 'error')
        finally:
            cursor.close()
            db.close()

    return render_template('searchdonor.html', donors=donors)

@app.route('/exchangeblood', methods=['GET', 'POST'])
def exchange_blood():
    if request.method == 'POST':
        patient_name = request.form['patient_name']
        blood_group = request.form['blood_group']
        contact_number = request.form['contact_number']
        location = request.form['location']
        donor_name = request.form['donor_name']
        donor_contact = request.form['donor_contact']

        if not patient_name or not blood_group or not contact_number or not location or not donor_name or not donor_contact:
            flash('Please fill in all the required fields.', 'error')
            return redirect('/exchangeblood')

        try:
            db = get_db_connection()
            if db is None:
                flash('Could not connect to the database.', 'error')
                return redirect('/exchangeblood')

            cursor = db.cursor()
            query = """
            INSERT INTO exchange_blood (patient_name, blood_group, contact_number, location, donor_name, donor_contact)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (patient_name, blood_group, contact_number, location, donor_name, donor_contact))
            db.commit()
            flash('Blood exchange request has been successfully submitted!', 'success')
        except pymysql.MySQLError as e:
            flash(f'Error inserting data: {e}', 'error')
        finally:
            cursor.close()
            db.close()

    return render_template('exchangeblood.html')

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
                flash('Could not connect to the database.', 'error')
                return redirect('/register')

            cursor = db.cursor()
            query = "INSERT INTO users (name, email, phone, password) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (name, email, phone, password))  # Storing plain text password
            db.commit()
            flash("Registration successful! Please log in.", "success")
        except pymysql.MySQLError as e:
            flash(f"Error registering user: {e}", "error")
        finally:
            if cursor:
                cursor.close()
            db.close()

        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        db = get_db_connection()
        if db is None:
            flash('Could not connect to the database.', 'error')
            return redirect('/login')

        cursor = db.cursor()
        query = "SELECT id, name, password FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()
        cursor.close()
        db.close()

        if user and user['password'] == password:  # Compare plain text password
            session['user_id'] = user['id']
            session['username'] = user['name']
            session.modified = True  # Ensures session updates
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials, please try again.", "error")

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        try:
            db = get_db_connection()
            if db is None:
                flash('Could not connect to the database.', 'error')
                return redirect('/dashboard')

            cursor = db.cursor()
            query = "SELECT * FROM need_blood ORDER BY required_date DESC"
            cursor.execute(query)
            requests = cursor.fetchall()

            query = "SELECT * FROM donate_blood ORDER BY donor_name"
            cursor.execute(query)
            donors = cursor.fetchall()

            cursor.close()
            db.close()

            return render_template('dashboard.html', username=session.get('username'), requests=requests, donors=donors)
        except pymysql.MySQLError as e:
            flash(f"Error fetching data for dashboard: {e}", "error")
            return redirect('/dashboard')
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out successfully.", "success")
    return redirect(url_for('login'))

@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
