from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
import boto3
import os
import re
import json
from botocore.exceptions import NoCredentialsError

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# AWS Configuration
S3_BUCKET = 'filestoragebucketgo'
S3_REGION = 'us-east-1'
SES_REGION = 'us-east-1'
SES_EMAIL = 'gyalavar@uab.edu'

s3_client = boto3.client('s3', region_name=S3_REGION)
ses_client = boto3.client('ses', region_name=SES_REGION)
# Lambda client
lambda_client = boto3.client('lambda', region_name=S3_REGION)

# RDS Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://admin:Sunnysamatha#1@database-1.clyayg0am7ei.us-east-1.rds.amazonaws.com/database-1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_TYPE'] = 'filesystem'
db = SQLAlchemy(app)
Session(app)

# DB Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class FileUpload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    file_name = db.Column(db.String(200), nullable=False)
    s3_url = db.Column(db.String(200), nullable=False)

with app.app_context():
    db.create_all()

# Password Validation
def validate_password(password):
    password_requirements = []
    if len(password) < 8:
        password_requirements.append('Password must be at least 8 characters long.')
    if not re.search(r'\d$', password):
        password_requirements.append('Password must end in a number.')
    if not re.search(r'[A-Z]', password):
        password_requirements.append('Password must contain at least one uppercase letter.')
    if not re.search(r'[a-z]', password):
        password_requirements.append('Password must contain at least one lowercase letter.')
    return password_requirements if password_requirements else True

# Home Page Login Check
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email_id = request.form['emailid']
        password = request.form['password']

        existing_user = User.query.filter_by(email=email_id).first()
        if existing_user:
            if password == existing_user.password:
                session['user_id'] = existing_user.id
                flash('Login Successful', 'success')
                return redirect(url_for('upload_file'))
            else:
                session['no_of_failed_attempts'] = session.get('no_of_failed_attempts', 0) + 1
                if session['no_of_failed_attempts'] >= 3:
                    flash('Password is invalid & 3 consecutive failed attempts', 'warning')
                    session['no_of_failed_attempts'] = 0
                else:
                    flash('Password is invalid', 'danger')
                return render_template('index.html')
        else:
            flash('User does not exist!', 'danger')
            return render_template('index.html')
    return render_template('index.html')

# Signup 
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('signup'))

        password_errors = validate_password(password)
        if password_errors != True:
            flash(' '.join(password_errors), 'danger')
            return redirect(url_for('signup'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email is already registered.', 'danger')
            return redirect(url_for('signup'))

        new_user = User(first_name=first_name, last_name=last_name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful!', 'success')
        return redirect(url_for('thankyou'))

    return render_template('signup.html')

@app.route('/thankyou')
def thankyou():
    return render_template('thankyou.html')

# File Upload Feature
@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    if 'user_id' not in session:
        flash('Please log in to upload files.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
        if file:
            file_name = file.filename
            user_id = session['user_id']
            s3_url = upload_to_s3(file, file_name)
            if s3_url:
                save_file_record(user_id, file_name, s3_url)
                email_addresses = request.form.get('email_addresses').split(',')
                # Invoke Lambda function to send emails
                lambda_payload = {
                    "file_url": s3_url,
                    "email_addresses": email_addresses
                }
                lambda_client.invoke(
                    FunctionName='emailsender',
                    InvocationType='Event',
                    Payload=json.dumps(lambda_payload)
                )
                flash('File uploaded and emails sent successfully!', 'success')
                return redirect(url_for('upload_file'))
            else:
                flash('File upload failed', 'danger')
                return redirect(request.url)
    return render_template('upload_file.html')

def upload_to_s3(file, file_name):
    try:
        s3_client.upload_fileobj(
            file,
            S3_BUCKET,
            file_name
        )
        s3_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{file_name}"
        return s3_url
    except NoCredentialsError:
        flash('Credentials not available', 'danger')
        return None

def save_file_record(user_id, file_name, s3_url):
    new_file = FileUpload(user_id=user_id, file_name=file_name, s3_url=s3_url)
    db.session.add(new_file)
    db.session.commit()

@app.route('/secretpage')
def secretpage():
    return render_template('secretpage.html')

@app.route('/report/<result>')
def report(result):
    return render_template('report.html', result=result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
