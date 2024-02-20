from flask import Flask, render_template, request, redirect, url_for, session
from prometheus_client import Counter, Histogram, generate_latest, Gauge
from flask_sqlalchemy import SQLAlchemy
import time
import psutil  # Import psutil for CPU and memory usage metrics

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

# Prometheus metrics
request_count = Counter('flask_http_requests_total', 'Total number of HTTP requests', ['method', 'endpoint', 'http_status'])
request_latency = Histogram('flask_http_request_duration_seconds', 'HTTP request latency in seconds', ['method', 'endpoint'])
login_counter = Counter('app_login_total', 'Total number of logins')
login_duration = Histogram('app_login_duration_seconds', 'Login duration in seconds')
app_uptime = Gauge('app_uptime_seconds', 'Duration since application start in seconds')
login_error_count = Counter('login_error_count_total', 'Total number of login errors')

# CPU and Memory Usage metrics
cpu_usage = Gauge('cpu_usage_percent', 'CPU usage percentage')
memory_usage = Gauge('memory_usage_percent', 'Memory usage percentage')

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
            login_counter.inc()
            logger.info(f'User {username} logged in successfully.')
            return redirect(url_for('dashboard'))
        else:
            login_error_count.inc() # Increment error count on failed login attempt
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
    request_count.labels(request.method, request.path, response.status_code).inc()
    request_latency.labels(request.method, request.path).observe(latency)
    return response

# Prometheus metrics endpoint
@app.route('/metrics')
def metrics():
    # Update app uptime metric
    app_uptime.set(time.time() - start_time)

    # Update CPU usage metric
    cpu_percent = psutil.cpu_percent()
    cpu_usage.set(cpu_percent)

    # Update memory usage metric
    mem_percent = psutil.virtual_memory().percent
    memory_usage.set(mem_percent)

    return generate_latest()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
