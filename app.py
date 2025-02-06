from flask import Flask, request, redirect, render_template, session, url_for, flash
import pymysql
import os
from flask_mail import Mail, Message

# Flask App Initialization
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "22852255")

# Database Configuration
db_config = {
    "host": "sql7.freesqldatabase.com",
    "port": 3306,
    "user": "sql7761392",
    "password": "uCMiaNNZfW",
    "database": "sql7761392"
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
        return pymysql.connect(
            **db_config, cursorclass=pymysql.cursors.DictCursor
        )
    except Exception as e:
        print(f"Database Connection Error: {e}")
        return None

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/donateblood', methods=['GET', 'POST'])
def donate_blood():
    if request.method == 'POST':
        donor_name = request.form['donor_name']
        blood_group = request.form['blood_group']
        contact_number = request.form['contact_number']
        location = request.form['location']

        if not all([donor_name, blood_group, contact_number, location]):
            flash('All fields are required!', 'error')
            return redirect('/donateblood')

        try:
            db = get_db_connection()
            if not db:
                raise Exception("Database Connection Failed")
            
            with db.cursor() as cursor:
                query = "INSERT INTO donate_blood (donor_name, blood_group, contact_number, location) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, (donor_name, blood_group, contact_number, location))
                db.commit()

            send_donation_email(donor_name, blood_group, contact_number, location)
            flash('Donation registered successfully!', 'success')
        except Exception as e:
            flash(f'Error: {e}', 'error')
        finally:
            db.close()

    return render_template('donateblood.html')

# Function to send email
def send_donation_email(donor_name, blood_group, contact_number, location):
    try:
        subject = "Blood Donation Registered"
        body = f"Dear {donor_name},\nThank you for registering. Your details:\nBlood Group: {blood_group}\nContact: {contact_number}\nLocation: {location}\n"
        msg = Message(subject, recipients=["recipient@example.com"])
        msg.body = body
        mail.send(msg)
        print("Email Sent Successfully")
    except Exception as e:
        print(f"Email Sending Error: {e}")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']  # Store password as plain text

        try:
            db = get_db_connection()
            if not db:
                raise Exception("Database Connection Failed")
            
            with db.cursor() as cursor:
                query = "INSERT INTO users (name, email, phone, password) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, (name, email, phone, password))
                db.commit()

            flash("Registration successful!", "success")
            return redirect(url_for('login'))
        except Exception as e:
            flash(f"Error: {e}", "error")
        finally:
            db.close()

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        try:
            db = get_db_connection()
            if not db:
                raise Exception("Database Connection Failed")

            with db.cursor() as cursor:
                query = "SELECT id, name, password FROM users WHERE email = %s"
                cursor.execute(query, (email,))
                user = cursor.fetchone()
            
            if user and user['password'] == password:  # Plain text password check
                session['user_id'] = user['id']
                session['username'] = user['name']
                flash("Login successful!", "success")
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid credentials.", "error")
        except Exception as e:
            flash(f"Error: {e}", "error")
        finally:
            db.close()
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        return render_template('dashboard.html', username=session.get('username'))
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for('login'))

@app.route('/search_donors', methods=['GET', 'POST'])
def search_donors():
    if request.method == 'POST':
        # Extract search parameters from the form
        blood_group = request.form.get('blood_group')
        location = request.form.get('location')

        try:
            db = get_db_connection()
            if not db:
                raise Exception("Database Connection Failed")
            
            with db.cursor() as cursor:
                query = "SELECT * FROM donate_blood WHERE blood_group = %s AND location = %s"
                cursor.execute(query, (blood_group, location))
                donors = cursor.fetchall()
            
            return render_template('donors_list.html', donors=donors)
        except Exception as e:
            flash(f"Error: {e}", "error")
        finally:
            if db:
                db.close()

    return render_template('search_donors.html')

# New route for requesting blood
@app.route('/request_blood', methods=['GET', 'POST'])
def request_blood():
    if request.method == 'POST':
        # Handle logic for requesting blood
        # You can add your form processing code here
        flash('Blood request submitted successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('request_blood.html')  # Render the page to request blood

# Main block to run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
