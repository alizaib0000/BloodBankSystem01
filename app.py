from flask import Flask, request, redirect, render_template, session, url_for, flash
import pymysql
from flask_mail import Mail, Message
import os

# Flask App Initialization
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "22852255")  # Secret key for sessions

# Detect environment (Local or Koyeb)
is_koyeb = os.environ.get("KOYEB") is not None

# Database Configuration (Local or Koyeb)
db_config = {
    "host": os.environ.get("KOYEB_DB_HOST") if is_koyeb else os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("KOYEB_DB_USER") if is_koyeb else os.environ.get("DB_USER", "root"),
    "password": os.environ.get("KOYEB_DB_PASSWORD") if is_koyeb else os.environ.get("DB_PASSWORD", "22852255"),
    "database": os.environ.get("KOYEB_DB_NAME") if is_koyeb else os.environ.get("DB_NAME", "blood_bank_system"),
    "port": int(os.environ.get("KOYEB_DB_PORT", 3306))
}

def get_db_connection():
    try:
        connection = pymysql.connect(
            host=db_config[""],
            user=db_config["user"],
            password=db_config["22852255"],
            database=db_config["blood_bank_system"],
            port=db_config["3306"],
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
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'bloodbanksystem018@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'mthk qeas wvua eomo')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'bloodbanksystem018@gmail.com')
mail = Mail(app)

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

        db = get_db_connection()
        if db is None:
            flash('Database connection failed!', 'error')
            return redirect('/needblood')

        try:
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

@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug= True is_koyeb)
