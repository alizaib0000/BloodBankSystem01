from flask import Flask, request, redirect, render_template, session, url_for, flash
import os
from flask_mail import Message, Mail

app = Flask(__name__)

# Secret Key (env se ayegi)
app.secret_key = os.getenv("SECRET_KEY", "fallback-secret")

# Routes
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/about')
def about():
    # Dummy data (database remove kiya hai)
    total_donations = 0
    donation_stats = []
    return render_template('about.html', total_donations=total_donations, donation_stats=donation_stats)

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/needblood', methods=['GET', 'POST'])
def need_blood():
    if request.method == 'POST':
        flash('Request submitted (DB removed version)', 'success')
        return redirect('/needblood')
    return render_template('needblood.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        flash("Registration successful (DB removed)", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['user_id'] = 1
        session['username'] = "Demo User"
        flash("Login successfully!")
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        return render_template('dashboard.html', username=session.get('username'))
    return redirect(url_for('login'))

# Mail config (env variables)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_DEFAULT_SENDER'] = os.getenv("MAIL_USERNAME")

mail = Mail(app)

@app.route('/donate_blood', methods=['POST'])
def donate_blood():
    if 'user_id' in session:
        try:
            msg = Message(
                subject="Blood Donation Confirmation",
                recipients=[request.form['email']]
            )
            msg.body = "Thank you for donating blood!"
            mail.send(msg)
            flash("Donation successful!", "success")
        except Exception as e:
            flash(f"Email failed: {str(e)}", "warning")
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for('login'))

# No cache
@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# Koyeb compatible run
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
