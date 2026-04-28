import os
from flask import Flask, request, redirect, render_template, session, url_for, flash
import pymysql
from flask_mail import Message, Mail

app = Flask(__name__)

# =========================
# 🔐 SECRET KEY
# =========================
app.secret_key = os.getenv("SECRET_KEY", "fallback_secret")

# =========================
# 📧 MAIL CONFIG
# =========================
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_DEFAULT_SENDER'] = os.getenv("MAIL_USERNAME")

mail = Mail(app)

# =========================
# 🗄 DATABASE FUNCTION
# =========================
def get_db():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT", 3306))
    )

# =========================
# ROUTES
# =========================

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/about')
def about():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT COUNT(*) FROM donations")
    total_donations = cursor.fetchone()[0]

    cursor.execute("SELECT blood_type, COUNT(*) FROM donations GROUP BY blood_type")
    donation_stats = cursor.fetchall()

    db.close()
    return render_template('about.html', total_donations=total_donations, donation_stats=donation_stats)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        db = get_db()
        cursor = db.cursor()

        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']

        cursor.execute("INSERT INTO users (name, email, phone, password) VALUES (%s,%s,%s,%s)",
                       (name, email, phone, password))
        db.commit()
        db.close()

        flash("Registered successfully!", "success")
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        db = get_db()
        cursor = db.cursor()

        email = request.form['email']
        password = request.form['password']

        cursor.execute("SELECT id, name, password FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        db.close()

        if user and user[2] == password:
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials", "error")

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    return render_template('dashboard.html', username=session['username'])


@app.route('/donate_blood', methods=['POST'])
def donate_blood():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor()

    name = request.form['name']
    email = request.form['email']
    blood_type = request.form['blood-type']

    cursor.execute(
        "INSERT INTO donations (name,email,blood_type,user_id) VALUES (%s,%s,%s,%s)",
        (name, email, blood_type, session['user_id'])
    )
    db.commit()
    db.close()

    # Email
    try:
        msg = Message("Donation Successful", recipients=[email])
        msg.body = f"Thank you {name} for donating blood!"
        mail.send(msg)
    except:
        pass

    flash("Donation successful", "success")
    return redirect(url_for('dashboard'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# =========================
# 🚀 RUN (Koyeb Compatible)
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
