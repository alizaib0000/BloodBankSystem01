from flask import Flask, request, redirect, render_template, session, url_for, flash
import pymysql
import os

# Flask App Initialization
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "22852255")  # Secret key for sessions

# Database Configuration (Local MySQL)
db_config = {
    "host": "localhost",  # Localhost MySQL server
    "port": 3306,         # Default MySQL port
    "user": "root",       # Default MySQL user
    "password": "your_password_here",  # Replace with your MySQL root password
    "database": "blood_bank_system"  # Replace with your actual database name
}

# Function to get a database connection
def get_db_connection():
    try:
        # Create the database connection
        connection = pymysql.connect(
            host=db_config['host'],
            port=db_config['port'],  # Ensure it's an integer
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database'],
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']

        db = get_db_connection()
        if db is None:
            flash('Could not connect to the database.', 'error')
            return redirect('/register')

        try:
            cursor = db.cursor()
            query = "INSERT INTO users (name, email, phone, password) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (name, email, phone, password))
            db.commit()
            flash("Registration successful! Please log in.", "success")
        except pymysql.MySQLError as e:
            flash(f"Error registering user: {e}", "error")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if db:
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

        try:
            cursor = db.cursor()
            query = "SELECT id, name, password FROM users WHERE email = %s"
            cursor.execute(query, (email,))
            user = cursor.fetchone()
            cursor.close()

            if user and user['password'] == password:
                session['user_id'] = user['id']
                session['username'] = user['name']
                flash("Login successfully!", "success")
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid credentials, please try again.", "error")
        except pymysql.MySQLError as e:
            flash(f"Error checking credentials: {e}", "error")
        finally:
            if db:
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
    flash("You have been logged out successfully.", "success")
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
