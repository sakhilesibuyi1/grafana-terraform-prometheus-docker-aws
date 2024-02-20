from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import time

import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:admin1223@postgresql/flask_db'  # Replace with your PostgreSQL connection URI
db = SQLAlchemy(app)
with app.app_context():
    # Create all tables
    db.create_all()

# Start time of the application
start_time = time.time()

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

@app.route('/')
def home():
    return 'Welcome to the Flask Prometheus Monitoring Example!'

@app.route('/login', methods=['GET', 'POST'])
@login_duration.time()
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        logger.info(f'password {password}')
        user = User.query.filter_by(username=username).first()
        if user:
            session['username'] = user.username
            logger.info(f'User {username} logged in successfully.')
            return redirect(url_for('dashboard'))
        else:
            logger.warning(f'Failed login attempt for username: {username}.')
            return render_template('login.html', error='Invalid username or password.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])
    return redirect(url_for('login'))

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    latency = time.time() - request.start_time
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
