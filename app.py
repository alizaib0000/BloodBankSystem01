from flask import Flask, request, redirect, render_template, session, url_for, flash,jsonify
import mysql.connector
import pymysql
from flask_mail import Message,Mail

# Flask App Initialization
app = Flask(__name__)

@app.route('/index')
def index():
    return render_template('index.html')  # Your HTML file name


app.secret_key = "22852255"  # Required for session management





# MySQL Configuration using Environment Variables
db_host = os.getenv("DB_HOST", "localhost")
db_user = os.getenv("DB_USER", "root")
db_password = os.getenv("DB_PASSWORD", "22852255")
db_name = os.getenv("DB_NAME", "bloodbank")

def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user=db_user,
        password="22852255",
        database="blood_bank_system"
        cursorclass=pymysql.cursors.DictCursor
    )



cursor = db.cursor()


@app.route('/features')
def features():
   return render_template('features.html')



@app.route('/about')
def about():
     # Query to get the total number of donations
    cursor.execute("SELECT COUNT(*) FROM donations")
    total_donations = cursor.fetchone()[0]  # Fetch the total count

    # Query to get the count of donations grouped by blood type
    cursor.execute("SELECT blood_type, COUNT(*) FROM donations GROUP BY blood_type")
    donation_stats = cursor.fetchall()  # Returns a list of tuples (e.g., [('A+', 10), ('O-', 5)])
    
    # Pass the data to the template
    return render_template('about.html', total_donations=total_donations, donation_stats=donation_stats)

@app.route('/contact')
def contact():
    return render_template('contact.html')  # Your About us file name




# Route for the "Need Blood" form
@app.route('/needblood', methods=['GET', 'POST'])
def need_blood():
    if request.method == 'POST':
        # Retrieve form data
        patient_name = request.form['patient_name']
        blood_group = request.form['blood_group']
        contact_number = request.form['contact_number']
        required_date = request.form['required_date']
        location = request.form['location']
        additional_info = request.form.get('additional_info', '')  # Default to empty string if not provided

        # Validate required fields
        if not patient_name or not blood_group or not contact_number or not required_date or not location:
            flash('Please fill in all the required fields.', 'error')
            return redirect('/needblood')

        try:
            # Prepare the SQL query
            query = """
            INSERT INTO need_blood (patient_name, blood_group, contact_number, required_date, location, additional_info)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            # Execute the query
            cursor = db.cursor()
            cursor.execute(query, (patient_name, blood_group, contact_number, required_date, location, additional_info))
            db.commit()  # Commit the transaction
            cursor.close()  # Close the cursor

            flash('Your blood request has been successfully submitted!', 'success')
            return redirect('/needblood')
        except mysql.connector.Error as e:
            flash(f'Error inserting data: {e}', 'error')
            return redirect('/needblood')

    # Render the form for GET request
    return render_template('needblood.html')




# Registration Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']  # Plain password

        # Save user to database
        query = "INSERT INTO users (name, email, phone, password) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (name, email, phone, password))
        db.commit() 
        
        # Flash message for successful registration
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))  # Redirect to login page after registration

    return render_template('register.html')  # Render registration form

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']  # Plain password input

        # Check if user exists
        query = "SELECT id, name, password FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()

        if user and user[2] == password:  # Compare input password with database password
            session['user_id'] = user[0]  # Save user ID in session
            session['username'] = user[1]  # Save username in session
            
            # Flash success message after successful login
            flash("Login successfully! ")

            return redirect(url_for('dashboard'))  # Redirect to dashboard on successful login
        else:
            flash("Invalid credentials, please try again.", "error")  # Flash message for invalid credentials  

    return render_template('login.html')


# Disable caching to prevent back button from showing error
@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


# Dashboard Route
@app.route('/dashboard')

def dashboard():
    if 'user_id' in session:
        username = session.get('username')  # Fetch the username from the session
        return render_template('dashboard.html', username=username)
        
    
    else:
        return redirect(url_for('login'))  # Redirect to login page if not logged in
        
    

# Flask-Mail configuration (only needed once in your app)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'bloodbanksystem018@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'mthk qeas wvua eomo'  # Replace with your email account password
app.config['MAIL_DEFAULT_SENDER'] = 'bloodbanksystem018@gmail.com'  # Sender email
mail = Mail(app)

# Blood donation route
@app.route('/donate_blood', methods=['POST'])
def donate_blood():
    if 'user_id' in session:
        # Retrieve form data
        name = request.form['name']
        email = request.form['email']  # User's email entered in the form
        phone = request.form['phone']
        gender = request.form['gender']
        age = request.form['age']
        blood_type = request.form['blood-type']
        address = request.form['address']
        last_donation = request.form['last-donation']

        # Insert the data into the database
        query = """
        INSERT INTO donations 
        (name, email, phone, gender, age, blood_type, address, last_donation, user_id) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (name, email, phone, gender, age, blood_type, address, last_donation, session['user_id']))
        db.commit()

        # Send email notification
        try:
            msg = Message(
                subject="Blood Donation Confirmation",
                recipients=[email]  # Email entered by the user in the form
            )
            msg.body = f"""
            Dear {name},

            Thank you for donating blood! Your generous contribution can save lives. 
            We have successfully recorded your donation details. 
            You are eligible to donate blood again after 3 months, and we will notify you when the time comes.

            Donation Details:
            - Name: {name}
            - Blood Type: {blood_type}
            - Last Donation Date: {last_donation}

            Thank you for being a lifesaver!

            Best regards,
            Blood Bank Team
            """
            mail.send(msg)
            flash("Blood donation successful! We will notify you after 3 months.", "success")
        except Exception as e:
            flash(f"Donation successful, but email notification failed: {str(e)}", "warning")

        # Redirect to the dashboard
        return redirect(url_for('dashboard'))
    else:
        flash("Please log in to access this feature.", "danger")
        return redirect(url_for('login'))


# Search Donors Route
@app.route('/search_donors', methods=['GET', 'POST'])
def search_donors():
    if 'user_id' in session:  # Ensure the user is logged in
        donors = None
        blood_type = None
        location = None

        if request.method == 'POST':
            # Get form inputs
            blood_type = request.form.get('blood-type')
            location = request.form.get('location', '').strip()

            # Build query
            query = "SELECT name, email, phone, blood_type, address FROM donations WHERE blood_type = %s"
            params = [blood_type]

            if location:
                query += " AND address LIKE %s"
                params.append(f"%{location}%")

            # Execute query
            cursor.execute(query, params)
            donors = cursor.fetchall()  # Fetch matching rows

        # Render the search form and results
        return render_template('dashboard.html', donors=donors, blood_type=blood_type, location=location, username=session.get('username'))
    else:
        # Redirect to login if user is not authenticated
        return redirect(url_for('login'))



# Request Blood Route
@app.route('/request_blood', methods=['POST'])
def request_blood():
    if 'user_id' in session:
        name = request.form['name']
        blood_type = request.form['blood-type']
        hospital = request.form['hospital']
        urgency = request.form['urgency']

        query = "INSERT INTO blood_requests (name, blood_type, hospital, urgency, user_id) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (name, blood_type, hospital, urgency, session['user_id']))
        db.commit()
        flash("Blood request submitted successfully!", "success")
        return redirect(url_for('dashboard'))

# Blood Exchange Route
@app.route('/exchange_blood', methods=['POST'])
def exchange_blood():
    if 'user_id' in session:
        name = request.form['name']
        blood_type = request.form['blood-type']
        reason = request.form['reason']

        query = "INSERT INTO blood_exchanges (name, blood_type, reason, user_id) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (name, blood_type, reason, session['user_id']))
        db.commit()
        flash("Blood exchange request submitted!", "success")
        return redirect(url_for('dashboard'))
        

# Disable caching to prevent back button from showing dashboard after logout
@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# Logout Route
@app.route('/logout')
def logout():
    session.clear()  # Clear all session data
    flash("You have been logged out successfully.", "success")
    return redirect(url_for('login'))  # Redirect to login after logout

# debug on host or port 80
import os
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))  # Ensure PORT is set
    app.run(host="0.0.0.0", port=port)
