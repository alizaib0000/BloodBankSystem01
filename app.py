from flask import Flask, request, redirect, render_template, session, url_for, flash, jsonify
import pymysql
from flask_mail import Mail, Message
import os

# Flask App Initialization
app = Flask(__name__)
app.secret_key = "22852255"

# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'bloodbanksystem018@gmail.com'
app.config['MAIL_PASSWORD'] = 'mthk qeas wvua eomo'
app.config['MAIL_DEFAULT_SENDER'] = 'bloodbanksystem018@gmail.com'
mail = Mail(app)

# MySQL Connection Function
def get_db_connection():
    return pymysql.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", "22852255"),
        database=os.environ.get("DB_NAME", "blood_bank_system"),
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/about')
def about():
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) AS total FROM donations")
    total_donations = cursor.fetchone()['total']
    cursor.execute("SELECT blood_type, COUNT(*) AS count FROM donations GROUP BY blood_type")
    donation_stats = cursor.fetchall()
    db.close()
    return render_template('about.html', total_donations=total_donations, donation_stats=donation_stats)

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/needblood', methods=['GET', 'POST'])
def need_blood():
    if request.method == 'POST':
        data = {key: request.form[key] for key in ['patient_name', 'blood_group', 'contact_number', 'required_date', 'location']}
        data['additional_info'] = request.form.get('additional_info', '')
        
        if not all(data.values()):
            flash('Please fill in all required fields.', 'error')
            return redirect(url_for('need_blood'))
        
        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute("INSERT INTO need_blood (patient_name, blood_group, contact_number, required_date, location, additional_info) VALUES (%s, %s, %s, %s, %s, %s)", tuple(data.values()))
            db.commit()
            flash('Blood request submitted successfully!', 'success')
        except Exception as e:
            flash(f'Error: {e}', 'error')
        finally:
            db.close()
    
    return render_template('needblood.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute("INSERT INTO users (name, email, phone, password) VALUES (%s, %s, %s, %s)", 
                           (request.form['name'], request.form['email'], request.form['phone'], request.form['password']))
            db.commit()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Registration error: {e}', 'error')
        finally:
            db.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT id, name, password FROM users WHERE email = %s", (request.form['email'],))
        user = cursor.fetchone()
        db.close()
        
        if user and user['password'] == request.form['password']:
            session['user_id'] = user['id']
            session['username'] = user['name']
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials.", "error")
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

@app.route('/donate_blood', methods=['POST'])
def donate_blood():
    if 'user_id' in session:
        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute("INSERT INTO donations (name, email, phone, gender, age, blood_type, address, last_donation, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                           (request.form['name'], request.form['email'], request.form['phone'], request.form['gender'], request.form['age'], request.form['blood-type'], request.form['address'], request.form['last-donation'], session['user_id']))
            db.commit()
            flash("Blood donation recorded successfully!", "success")
        except Exception as e:
            flash(f'Error: {e}', 'error')
        finally:
            db.close()
    else:
        flash("Please log in.", "danger")
    return redirect(url_for('dashboard'))

@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
