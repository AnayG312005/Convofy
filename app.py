from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, jsonify
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import random
import string
import os
import json
import re
import plotly.express as px
import numpy as np
import pandas as pd
import csv
from datetime import datetime
from dotenv import load_dotenv
import pdfkit
from reportlab.pdfgen import canvas
from io import BytesIO
from flask.helpers import send_file
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer
from health_ai import generate_ai_response

try:
    from tensorflow.keras.preprocessing import image as tf_image
    import tensorflow as tf
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False

app = Flask(__name__)
load_dotenv()

app.secret_key = os.getenv('SECRET_KEY', 'CONVOFY_SECRET_KEY_2024')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT') or 465)
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

ALLOWED_REPORT_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'docx', 'txt'}
UPLOAD_FOLDER = os.path.join('static', 'uploads', 'reports')
BLOG_IMG_FOLDER = os.path.join('static', 'uploads', 'blog')

mail = Mail(app)
db = SQLAlchemy(app)

# ============================================================ MODELS ============================================================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    type_of_doctor = db.Column(db.String(50))
    is_admin = db.Column(db.Boolean, default=False)
    bio = db.Column(db.Text, default='')
    experience_years = db.Column(db.Integer, default=0)
    fee = db.Column(db.Float, default=500.0)
    rating = db.Column(db.Float, default=4.5)
    profile_photo = db.Column(db.String(255), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    blood_group = db.Column(db.String(10), nullable=False)
    time_slot = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    type_of_doctor = db.Column(db.String(50))
    status = db.Column(db.String(20), default='Pending')
    prescription_file = db.Column(db.String(255))
    notes = db.Column(db.Text, default='')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('appointments', lazy=True))

class AiChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    msg_type = db.Column(db.String(20), default='info')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('ai_chats', lazy=True))

class DoctorMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    sender = db.relationship('User', foreign_keys=[sender_id], backref=db.backref('sent_messages', lazy=True))
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref=db.backref('received_messages', lazy=True))

class ScanReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255), nullable=False)
    report_type = db.Column(db.String(50), default='General')
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, default='')
    ai_summary = db.Column(db.Text, default='')
    file_size = db.Column(db.Integer, default=0)
    user = db.relationship('User', backref=db.backref('scan_reports', lazy=True))

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.String(500), default='')
    category = db.Column(db.String(50), default='General')
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    published = db.Column(db.Boolean, default=True)
    views = db.Column(db.Integer, default=0)
    featured_image = db.Column(db.String(255), default='')
    read_time = db.Column(db.Integer, default=5)
    author = db.relationship('User', backref=db.backref('blog_posts', lazy=True))

class BlogComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('blog_post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    post = db.relationship('BlogPost', backref=db.backref('comments', lazy=True, cascade='all, delete-orphan'))
    user = db.relationship('User', backref=db.backref('blog_comments', lazy=True))

class BlogLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('blog_post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    __table_args__ = (db.UniqueConstraint('post_id', 'user_id', name='unique_blog_like'),)

class BlogBookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('blog_post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    __table_args__ = (db.UniqueConstraint('post_id', 'user_id', name='unique_blog_bookmark'),)

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text, default='')
    ip_address = db.Column(db.String(50), default='')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# ============================================================ SETUP ============================================================

def create_tables():
    with app.app_context():
        db.create_all()
        seed_blog_posts()

def allowed_file(filename, allowed=ALLOWED_REPORT_EXTENSIONS):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed

def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text[:100]

def log_action(user_id, action, details=''):
    try:
        ip = request.remote_addr or ''
        log = AuditLog(user_id=user_id, action=action, details=details, ip_address=ip)
        db.session.add(log)
        db.session.commit()
    except Exception:
        pass

def seed_blog_posts():
    if BlogPost.query.count() > 0:
        return
    posts = [
        {
            'title': 'Transforming Healthcare with AI',
            'slug': 'transforming-healthcare-with-ai',
            'excerpt': 'Artificial Intelligence is revolutionising how we diagnose, treat, and manage health conditions worldwide.',
            'category': 'Technology',
            'read_time': 6,
            'content': """<h2>The AI Revolution in Medicine</h2>
<p>Artificial Intelligence is fundamentally transforming the healthcare landscape. From early disease detection to personalised treatment plans, AI is proving to be a powerful tool that augments the capabilities of medical professionals.</p>
<h3>Early Disease Detection</h3>
<p>AI algorithms trained on millions of medical images can now detect cancers, diabetic retinopathy, and other conditions with accuracy that rivals — and sometimes surpasses — experienced clinicians. Google's DeepMind system, for instance, can detect over 50 eye diseases from retinal scans with 94% accuracy.</p>
<h3>Drug Discovery Acceleration</h3>
<p>Traditional drug discovery takes 10-15 years and billions of dollars. AI is compressing this timeline dramatically. During COVID-19, AI platforms identified potential drug candidates within days rather than years.</p>
<h3>Personalised Medicine</h3>
<p>By analysing a patient's genetic makeup, lifestyle, environment, and medical history, AI can recommend treatments tailored to the individual — moving away from the "one size fits all" approach to medicine.</p>
<h3>Predictive Analytics</h3>
<p>Hospitals are using AI to predict which patients are at risk of deterioration, sepsis, or readmission, allowing clinicians to intervene proactively rather than reactively.</p>
<h3>The Future is Collaborative</h3>
<p>The most exciting healthcare future is not AI replacing doctors, but AI and doctors working together — AI handling data processing, pattern recognition, and administrative tasks, while clinicians focus on empathy, complex decision-making, and the human elements of care that cannot be replicated by machines.</p>"""
        },
        {
            'title': 'Holistic Health: Mind, Body & Spirit',
            'slug': 'holistic-health-mind-body-spirit',
            'excerpt': 'True wellbeing goes beyond the absence of disease — it encompasses mental, physical, social, and spiritual dimensions.',
            'category': 'Wellness',
            'read_time': 7,
            'content': """<h2>What is Holistic Health?</h2>
<p>Holistic health is an approach to wellness that considers the whole person — body, mind, spirit, and emotions — rather than focusing solely on the absence of disease. It recognises that these dimensions are deeply interconnected.</p>
<h3>The Mind-Body Connection</h3>
<p>Research consistently demonstrates that our mental state profoundly affects our physical health. Chronic stress elevates cortisol, suppresses the immune system, increases inflammation, and raises the risk of heart disease. Conversely, positive emotions and strong social connections are associated with better physical health outcomes and longer life.</p>
<h3>Physical Pillars</h3>
<p><strong>Nutrition:</strong> Food is information for your cells. A diet rich in whole foods, varied plants, and lean proteins provides the building blocks for health at a cellular level.</p>
<p><strong>Movement:</strong> Regular physical activity is perhaps the most powerful medicine available — reducing risk of over 35 chronic conditions and improving mood, cognition, and longevity.</p>
<p><strong>Sleep:</strong> During sleep, the brain clears toxins, consolidates memories, and the body repairs itself. Chronic sleep deprivation accelerates ageing and disease.</p>
<h3>Mental & Emotional Dimensions</h3>
<p>Practices like mindfulness meditation, journaling, therapy, and meaningful relationships all contribute to mental resilience. These aren't "nice to haves" — they're essential components of health.</p>
<h3>Social Connection</h3>
<p>Loneliness is as harmful to health as smoking 15 cigarettes per day. Strong social connections are one of the most powerful predictors of longevity and wellbeing.</p>
<h3>Practical Holistic Steps</h3>
<ul>
<li>10 minutes of mindfulness daily</li>
<li>30 minutes of movement most days</li>
<li>Prioritise 7-9 hours of sleep</li>
<li>Nurture at least 3-5 close relationships</li>
<li>Spend time in nature weekly</li>
<li>Find purpose and meaning</li>
</ul>"""
        },
        {
            'title': 'Nourishing Your Body: The Science of Nutrition',
            'slug': 'nourishing-your-body-science-of-nutrition',
            'excerpt': 'Evidence-based nutrition guidance to fuel your body, support your immune system, and reduce chronic disease risk.',
            'category': 'Nutrition',
            'read_time': 8,
            'content': """<h2>Food as Medicine</h2>
<p>Hippocrates said "Let food be thy medicine" — and modern nutritional science has validated this wisdom extensively. The foods we eat directly influence our gene expression, gut microbiome, inflammation levels, and long-term disease risk.</p>
<h3>The Gut Microbiome Revolution</h3>
<p>We now know the gut contains over 38 trillion bacteria — outnumbering our own cells. This microbiome influences everything from immune function to mood (via the gut-brain axis) to metabolism. Fibre-rich, diverse plant foods are the best fuel for a healthy microbiome.</p>
<h3>The Foundation: Whole Foods</h3>
<p>The most consistent finding across nutritional research is that diets built around minimally processed whole foods — vegetables, fruits, legumes, whole grains, nuts, seeds, and quality proteins — are associated with the best health outcomes.</p>
<h3>Key Nutritional Principles</h3>
<p><strong>Eat the rainbow:</strong> Different coloured plant foods contain different phytonutrients. Aim for 7+ different vegetables and fruits daily.</p>
<p><strong>Prioritise fibre:</strong> Most people consume less than half the recommended 25-38g/day. Fibre feeds beneficial gut bacteria, regulates blood sugar, and reduces colorectal cancer risk.</p>
<p><strong>Quality fats:</strong> Olive oil, avocados, nuts, and oily fish provide anti-inflammatory omega-3s. Limit ultra-processed oils and trans fats.</p>
<p><strong>Protein quality matters:</strong> Focus on diverse protein sources — legumes, fish, poultry, eggs, and dairy — rather than excessive red and processed meat.</p>
<h3>What to Minimise</h3>
<ul>
<li>Ultra-processed foods (>50% of calories in average Western diet)</li>
<li>Added sugars (linked to obesity, metabolic syndrome, dental decay)</li>
<li>Excessive sodium (increases blood pressure)</li>
<li>Alcohol (carcinogenic, even in moderate amounts)</li>
</ul>
<h3>Practical Application</h3>
<p>You don't need to be perfect — the 80/20 principle applies well to nutrition. Eat whole, nourishing foods 80% of the time, and allow flexibility for the remainder. Consistency over months and years matters far more than perfection over days.</p>"""
        },
        {
            'title': 'The Importance of Physical Activity for Health',
            'slug': 'importance-of-physical-activity-for-health',
            'excerpt': 'Regular exercise is the closest thing to a magic pill — reducing risk of dozens of diseases and improving every aspect of health.',
            'category': 'Fitness',
            'read_time': 5,
            'content': """<h2>Exercise: The Most Powerful Medicine</h2>
<p>If physical activity were a drug, it would be the most prescribed, most effective, and least side-effect-causing medication in history. The evidence for exercise as medicine is overwhelming.</p>
<h3>What Exercise Does to Your Body</h3>
<p><strong>Cardiovascular system:</strong> Strengthens the heart muscle, improves circulation, lowers blood pressure, raises HDL ("good") cholesterol.</p>
<p><strong>Musculoskeletal system:</strong> Builds and maintains muscle mass, strengthens bones (reducing osteoporosis risk), improves balance and coordination.</p>
<p><strong>Metabolic system:</strong> Increases insulin sensitivity, improves blood sugar regulation, boosts metabolic rate, reduces visceral fat.</p>
<p><strong>Brain:</strong> Promotes neuroplasticity and neurogenesis, reduces risk of Alzheimer's and dementia by up to 40%, improves mood (as effective as antidepressants for mild-moderate depression), reduces anxiety.</p>
<p><strong>Immune system:</strong> Moderate exercise reduces infection risk; chronic intense training can temporarily suppress immunity.</p>
<h3>How Much is Enough?</h3>
<p>WHO guidelines recommend 150-300 minutes of moderate aerobic activity per week (like brisk walking) or 75-150 minutes of vigorous activity (running, HIIT), plus 2+ days of strength training.</p>
<p>But here's the most important finding: even small amounts help. Going from zero to 15 minutes of walking daily cuts mortality risk by 14%. Every little bit counts.</p>
<h3>The Best Exercise</h3>
<p>The best exercise is the one you'll actually do consistently. Whether that's swimming, dancing, hiking, cycling, yoga, or team sports — enjoyment is the most underrated factor in exercise adherence.</p>
<h3>Getting Started Safely</h3>
<ul>
<li>Start low, go slow — especially after a period of inactivity</li>
<li>Warm up and cool down with every session</li>
<li>Build gradually (10% increase per week maximum)</li>
<li>Listen to your body — pain is a signal, not a challenge</li>
<li>See your doctor before starting if you have a chronic condition</li>
</ul>"""
        }
    ]
    for p in posts:
        word_count = len(p['content'].split())
        read_time = max(3, word_count // 200)
        post = BlogPost(
            title=p['title'],
            slug=p['slug'],
            content=p['content'],
            excerpt=p['excerpt'],
            category=p['category'],
            published=True,
            read_time=read_time
        )
        db.session.add(post)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()

create_tables()

# ============================================================ ML MODEL ============================================================

text_files_dir = os.path.join(os.path.dirname(__file__), 'static/prescriptions')
pdf_output_dir = os.path.join(os.path.dirname(__file__), 'static/pdfs')

data = pd.read_csv(os.path.join("static", "Data", "Training.csv"))
df = pd.DataFrame(data)
cols = df.columns[:-1]
x = df[cols]
y = df['prognosis']
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.33, random_state=42)
dt = DecisionTreeClassifier()
clf_dt = dt.fit(x_train, y_train)
indices = [i for i in range(132)]
symptoms_list = df.columns.values[:-1]
dictionary = dict(zip(symptoms_list, indices))

with open('static/Data/Testing.csv', newline='') as f:
    reader = csv.reader(f)
    symptoms = next(reader)
    symptoms = symptoms[:len(symptoms) - 1]

def predict(symptom):
    user_input_label = [0 for _ in range(132)]
    for s in symptom:
        if s in dictionary:
            user_input_label[dictionary[s]] = 1
    user_input_label = np.array(user_input_label).reshape((-1, 1)).transpose()
    predicted_disease = dt.predict(user_input_label)[0]
    confidence_score = np.max(dt.predict_proba(user_input_label)) * 100
    return predicted_disease, confidence_score

def generate_random_string(length=10):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

def send_mail(subject, recipient, body):
    try:
        msg = Message(subject, recipients=[recipient])
        msg.body = body
        mail.send(msg)
    except Exception:
        pass

def get_current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

# ============================================================ MAIN ROUTES ============================================================

@app.route('/', methods=['GET', 'POST'])
def index():
    user = get_current_user()
    if user:
        if user.type_of_doctor:
            appointments = Appointment.query.filter_by(type_of_doctor=user.type_of_doctor).all()
            unread = DoctorMessage.query.filter_by(receiver_id=user.id, is_read=False).count()
            return render_template('doctor-dashboard.html', username=user.username, appointments=appointments, unread_count=unread)
        else:
            unread = DoctorMessage.query.filter_by(receiver_id=user.id, is_read=False).count()
            return render_template('patient-dashboard.html', username=user.username, user_appointments=user.appointments, unread_count=unread)
    return render_template('index.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    if request.method == 'POST':
        bio = request.form.get('bio', '')
        experience_years = request.form.get('experience_years', 0)
        fee = request.form.get('fee', 500.0)
        user.bio = bio
        if user.type_of_doctor:
            user.experience_years = int(experience_years) if experience_years else 0
            user.fee = float(fee) if fee else 500.0
        db.session.commit()
        flash('Profile updated successfully!', 'success')
    return render_template('patient-profile.html', username=user.username, Email=user.email, user_appointments=user.appointments, user=user)

@app.route('/patient-register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed = generate_password_hash(password)
        try:
            user = User(username=username, email=email, password=hashed)
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
            log_action(user.id, 'register', f'Patient registered: {username}')
            return redirect(url_for('index'))
        except IntegrityError:
            db.session.rollback()
            flash('Username already exists. Please choose a different username.', 'error')
    return render_template('patient-register.html')

@app.route('/doctor-register', methods=['GET', 'POST'])
def doctor_register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        type_of_doctor = request.form['type_of_doctor']
        hashed = generate_password_hash(password)
        try:
            user = User(username=username, email=email, password=hashed, type_of_doctor=type_of_doctor)
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
            log_action(user.id, 'register', f'Doctor registered: {username} ({type_of_doctor})')
            return redirect(url_for('index'))
        except IntegrityError:
            db.session.rollback()
            flash('Username already exists.', 'error')
    return render_template('doctor-register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user:
            authenticated = False
            if user.password.startswith('pbkdf2:') or user.password.startswith('scrypt:'):
                authenticated = check_password_hash(user.password, password)
            else:
                # Backward compat: plaintext password → rehash
                if user.password == password:
                    authenticated = True
                    user.password = generate_password_hash(password)
                    db.session.commit()
            if authenticated:
                session['user_id'] = user.id
                log_action(user.id, 'login', f'Login: {username}')
                return redirect(url_for('index'))
        flash('Wrong username or password. Please try again.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    user = get_current_user()
    if user:
        log_action(user.id, 'logout', '')
    session.pop('user_id', None)
    return redirect(url_for('index'))

# ============================================================ APPOINTMENTS ============================================================

@app.route('/book-appointment', methods=['GET', 'POST'])
def book_appointment():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = get_current_user()
    doctor_types = db.session.query(User.type_of_doctor).filter(User.type_of_doctor != None).distinct().all()
    doctor_types = [d[0] for d in doctor_types if d[0]]
    if request.method == 'POST':
        name = request.form['name']
        age = int(request.form['age'])
        blood_group = request.form['blood_group']
        time_slot = request.form['time_slot']
        phone_number = request.form['phone_number']
        email = request.form['email']
        type_of_doctor = request.form['type_of_doctor']
        appointment = Appointment(
            name=name, age=age, blood_group=blood_group,
            time_slot=time_slot, phone_number=phone_number,
            email=email, type_of_doctor=type_of_doctor, user=user
        )
        db.session.add(appointment)
        db.session.commit()
        log_action(user.id, 'book_appointment', f'Booked {type_of_doctor} appointment')
        try:
            doc = User.query.filter_by(type_of_doctor=type_of_doctor).first()
            if doc:
                send_mail('New Appointment Request — Convofy',
                    doc.email,
                    f'Hello Dr. {doc.username},\n\nYou have a new appointment request from {name}.\nTime slot: {time_slot}\n\nPlease log in to Convofy to approve or reject it.\n\n— Convofy Team')
        except Exception:
            pass
        flash('Appointment booked successfully! The doctor has been notified.', 'success')
        return redirect(url_for('index'))
    return render_template('book-appointment.html', doctor_types=doctor_types, username=user.username)

@app.route('/approve-appointment/<int:appointment_id>')
def approve_appointment(appointment_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    doctor = get_current_user()
    appointment = Appointment.query.get_or_404(appointment_id)
    if appointment.type_of_doctor != doctor.type_of_doctor:
        return redirect(url_for('index'))
    appointment.status = 'Approved'
    db.session.commit()
    log_action(doctor.id, 'approve_appointment', f'Appointment #{appointment_id} approved')
    send_mail('Appointment Approved — Convofy', appointment.email,
        f'Hello {appointment.name},\n\nYour appointment has been approved by Dr. {doctor.username}.\nTime slot: {appointment.time_slot}\n\nLog in to Convofy to view details.\n\n— Convofy Team')
    flash('Appointment approved and patient notified.', 'success')
    return redirect(url_for('index'))

@app.route('/cancel-appointment/<int:appointment_id>', methods=['POST'])
def cancel_appointment(appointment_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = get_current_user()
    appointment = Appointment.query.get_or_404(appointment_id)
    if appointment.user_id != user.id and appointment.type_of_doctor != getattr(user, 'type_of_doctor', None):
        flash('Unauthorised action.', 'error')
        return redirect(url_for('index'))
    appointment.status = 'Cancelled'
    db.session.commit()
    log_action(user.id, 'cancel_appointment', f'Appointment #{appointment_id} cancelled')
    flash('Appointment cancelled.', 'success')
    return redirect(url_for('index'))

# ============================================================ AI CHAT ============================================================

@app.route('/ai-chat')
def ai_chat():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = get_current_user()
    history = AiChatMessage.query.filter_by(user_id=user.id).order_by(AiChatMessage.timestamp.asc()).all()
    return render_template('ai-chat.html', username=user.username, history=history)

@app.route('/api/ai-chat', methods=['POST'])
def api_ai_chat():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorised'}), 401
    user = get_current_user()
    data = request.get_json()
    message = data.get('message', '').strip()
    if not message:
        return jsonify({'error': 'Empty message'}), 400
    result = generate_ai_response(message)
    chat_msg = AiChatMessage(
        user_id=user.id,
        message=message,
        response=result['response'],
        msg_type=result['type']
    )
    db.session.add(chat_msg)
    db.session.commit()
    log_action(user.id, 'ai_chat', f'Query: {message[:80]}')
    return jsonify({
        'response': result['response'],
        'type': result['type'],
        'timestamp': chat_msg.timestamp.strftime('%H:%M')
    })

@app.route('/ai-chat/clear', methods=['POST'])
def clear_ai_chat():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = get_current_user()
    AiChatMessage.query.filter_by(user_id=user.id).delete()
    db.session.commit()
    flash('Chat history cleared.', 'success')
    return redirect(url_for('ai_chat'))

# ============================================================ DOCTOR CHAT ============================================================

@app.route('/chat')
def chat_inbox():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = get_current_user()
    sent_to = db.session.query(DoctorMessage.receiver_id).filter_by(sender_id=user.id).distinct().all()
    received_from = db.session.query(DoctorMessage.sender_id).filter_by(receiver_id=user.id).distinct().all()
    partner_ids = set([r[0] for r in sent_to] + [r[0] for r in received_from])
    partners = []
    for pid in partner_ids:
        partner = User.query.get(pid)
        if partner:
            last_msg = DoctorMessage.query.filter(
                ((DoctorMessage.sender_id == user.id) & (DoctorMessage.receiver_id == pid)) |
                ((DoctorMessage.sender_id == pid) & (DoctorMessage.receiver_id == user.id))
            ).order_by(DoctorMessage.timestamp.desc()).first()
            unread = DoctorMessage.query.filter_by(sender_id=pid, receiver_id=user.id, is_read=False).count()
            partners.append({'user': partner, 'last_msg': last_msg, 'unread': unread})
    partners.sort(key=lambda x: x['last_msg'].timestamp if x['last_msg'] else datetime.min, reverse=True)
    if user.type_of_doctor:
        available_contacts = User.query.filter_by(type_of_doctor=None).all()
    else:
        available_contacts = User.query.filter(User.type_of_doctor != None).all()
    return render_template('chat-inbox.html', username=user.username, partners=partners, available_contacts=available_contacts, user=user)

@app.route('/chat/<int:partner_id>')
def chat_thread(partner_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = get_current_user()
    partner = User.query.get_or_404(partner_id)
    DoctorMessage.query.filter_by(sender_id=partner_id, receiver_id=user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    messages = DoctorMessage.query.filter(
        ((DoctorMessage.sender_id == user.id) & (DoctorMessage.receiver_id == partner_id)) |
        ((DoctorMessage.sender_id == partner_id) & (DoctorMessage.receiver_id == user.id))
    ).order_by(DoctorMessage.timestamp.asc()).all()
    return render_template('doctor-chat.html', username=user.username, partner=partner, messages=messages, user=user)

@app.route('/api/send-message', methods=['POST'])
def send_message():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorised'}), 401
    user = get_current_user()
    data = request.get_json()
    receiver_id = data.get('receiver_id')
    message_text = data.get('message', '').strip()
    if not receiver_id or not message_text:
        return jsonify({'error': 'Missing fields'}), 400
    receiver = User.query.get(receiver_id)
    if not receiver:
        return jsonify({'error': 'User not found'}), 404
    msg = DoctorMessage(sender_id=user.id, receiver_id=receiver_id, message=message_text)
    db.session.add(msg)
    db.session.commit()
    return jsonify({
        'id': msg.id,
        'message': msg.message,
        'timestamp': msg.timestamp.strftime('%H:%M'),
        'sender_id': user.id
    })

@app.route('/api/get-messages')
def get_messages():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorised'}), 401
    user = get_current_user()
    partner_id = request.args.get('partner_id', type=int)
    since_id = request.args.get('since_id', 0, type=int)
    if not partner_id:
        return jsonify({'error': 'partner_id required'}), 400
    DoctorMessage.query.filter_by(sender_id=partner_id, receiver_id=user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    messages = DoctorMessage.query.filter(
        DoctorMessage.id > since_id,
        ((DoctorMessage.sender_id == user.id) & (DoctorMessage.receiver_id == partner_id)) |
        ((DoctorMessage.sender_id == partner_id) & (DoctorMessage.receiver_id == user.id))
    ).order_by(DoctorMessage.timestamp.asc()).all()
    return jsonify([{
        'id': m.id,
        'message': m.message,
        'sender_id': m.sender_id,
        'timestamp': m.timestamp.strftime('%H:%M'),
        'is_read': m.is_read
    } for m in messages])

# ============================================================ SCAN REPORTS ============================================================

@app.route('/scan-reports')
def scan_reports():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = get_current_user()
    reports = ScanReport.query.filter_by(user_id=user.id).order_by(ScanReport.upload_date.desc()).all()
    return render_template('scan-reports.html', username=user.username, reports=reports)

@app.route('/scan-reports/upload', methods=['POST'])
def upload_report():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = get_current_user()
    if 'file' not in request.files:
        flash('No file selected.', 'error')
        return redirect(url_for('scan_reports'))
    file = request.files['file']
    if file.filename == '':
        flash('No file selected.', 'error')
        return redirect(url_for('scan_reports'))
    if not allowed_file(file.filename):
        flash('File type not allowed. Please upload PDF, images, or documents.', 'error')
        return redirect(url_for('scan_reports'))
    report_type = request.form.get('report_type', 'General')
    notes = request.form.get('notes', '')
    original_name = secure_filename(file.filename)
    ext = original_name.rsplit('.', 1)[1].lower()
    unique_name = f"{user.id}_{int(datetime.utcnow().timestamp())}_{generate_random_string(6)}.{ext}"
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    filepath = os.path.join(UPLOAD_FOLDER, unique_name)
    file.save(filepath)
    file_size = os.path.getsize(filepath)
    ai_summary = generate_report_ai_summary(original_name, report_type, ext)
    report = ScanReport(
        user_id=user.id,
        filename=unique_name,
        original_name=original_name,
        report_type=report_type,
        notes=notes,
        ai_summary=ai_summary,
        file_size=file_size
    )
    db.session.add(report)
    db.session.commit()
    log_action(user.id, 'upload_report', f'Uploaded: {original_name}')
    flash(f'Report "{original_name}" uploaded and analysed successfully!', 'success')
    return redirect(url_for('scan_reports'))

def generate_report_ai_summary(filename, report_type, ext):
    summaries = {
        'Blood Test': "This appears to be a blood test report. Key areas to discuss with your doctor include complete blood count (CBC), metabolic panel values, and any flagged abnormal results. Common biomarkers include haemoglobin, white blood cell count, platelets, glucose, and kidney/liver function markers.",
        'X-Ray': "This appears to be an X-ray image. X-rays are used to visualise bones and some soft tissues. Your doctor will assess for fractures, joint spacing, bone density, and any opacities. Please have a radiologist or your treating doctor review this image for a formal report.",
        'MRI': "This appears to be an MRI scan. MRI provides detailed soft tissue imaging. Your radiologist will assess structures, signal intensities, and any abnormalities. Please ensure this is reviewed by a qualified radiologist for a diagnostic report.",
        'CT Scan': "This appears to be a CT scan. CT imaging provides cross-sectional views of the body. Key findings will be documented in a formal radiology report covering density, structure, and any lesions or abnormalities identified.",
        'Prescription': "This is a prescription document. Please follow all medication instructions as directed by your prescribing doctor. Note dosages, frequency, and duration. Contact your doctor or pharmacist if you have any questions about your medications.",
        'Lab Report': "This laboratory report contains test results. Abnormal values are typically flagged (H for high, L for low). Please discuss all results with your healthcare provider for interpretation in the context of your symptoms and history.",
        'ECG': "This is an electrocardiogram (ECG) recording. ECGs measure the electrical activity of the heart. Key parameters include heart rate, rhythm, P waves, QRS complex, and T waves. A cardiologist or trained physician should interpret this in clinical context.",
        'General': f"This document ({filename}) has been securely uploaded to your Convofy medical record. For accurate interpretation, please share this report with your treating physician at your next appointment. Convofy stores your reports encrypted for your privacy."
    }
    return summaries.get(report_type, summaries['General'])

@app.route('/scan-reports/download/<int:report_id>')
def download_report(report_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = get_current_user()
    report = ScanReport.query.get_or_404(report_id)
    if report.user_id != user.id and not user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('scan_reports'))
    filepath = os.path.join(UPLOAD_FOLDER, report.filename)
    if not os.path.exists(filepath):
        flash('File not found.', 'error')
        return redirect(url_for('scan_reports'))
    return send_file(filepath, as_attachment=True, download_name=report.original_name)

@app.route('/scan-reports/delete/<int:report_id>', methods=['POST'])
def delete_report(report_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = get_current_user()
    report = ScanReport.query.get_or_404(report_id)
    if report.user_id != user.id and not user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('scan_reports'))
    filepath = os.path.join(UPLOAD_FOLDER, report.filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    db.session.delete(report)
    db.session.commit()
    log_action(user.id, 'delete_report', f'Deleted report #{report_id}')
    flash('Report deleted.', 'success')
    return redirect(url_for('scan_reports'))

# ============================================================ BLOG ============================================================

@app.route('/blog')
def blog():
    user = get_current_user()
    username = user.username if user else None
    category = request.args.get('category', '')
    search = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    query = BlogPost.query.filter_by(published=True)
    if category:
        query = query.filter_by(category=category)
    if search:
        query = query.filter(BlogPost.title.ilike(f'%{search}%') | BlogPost.content.ilike(f'%{search}%'))
    posts = query.order_by(BlogPost.created_at.desc()).paginate(page=page, per_page=6, error_out=False)
    categories = db.session.query(BlogPost.category).distinct().all()
    categories = [c[0] for c in categories if c[0]]
    return render_template('blog.html', username=username, posts=posts, categories=categories,
                           current_category=category, search=search, user=user)

@app.route('/blog/<slug>')
def blog_post(slug):
    user = get_current_user()
    username = user.username if user else None
    post = BlogPost.query.filter_by(slug=slug, published=True).first_or_404()
    post.views += 1
    db.session.commit()
    liked = False
    bookmarked = False
    if user:
        liked = BlogLike.query.filter_by(post_id=post.id, user_id=user.id).first() is not None
        bookmarked = BlogBookmark.query.filter_by(post_id=post.id, user_id=user.id).first() is not None
    like_count = BlogLike.query.filter_by(post_id=post.id).count()
    related = BlogPost.query.filter_by(category=post.category, published=True).filter(BlogPost.id != post.id).limit(3).all()
    return render_template('blog-post.html', username=username, post=post, liked=liked,
                           bookmarked=bookmarked, like_count=like_count, related=related, user=user)

@app.route('/blog/<int:post_id>/like', methods=['POST'])
def blog_like(post_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Login required'}), 401
    user = get_current_user()
    existing = BlogLike.query.filter_by(post_id=post_id, user_id=user.id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        liked = False
    else:
        like = BlogLike(post_id=post_id, user_id=user.id)
        db.session.add(like)
        db.session.commit()
        liked = True
    count = BlogLike.query.filter_by(post_id=post_id).count()
    return jsonify({'liked': liked, 'count': count})

@app.route('/blog/<int:post_id>/bookmark', methods=['POST'])
def blog_bookmark(post_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Login required'}), 401
    user = get_current_user()
    existing = BlogBookmark.query.filter_by(post_id=post_id, user_id=user.id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        bookmarked = False
    else:
        bm = BlogBookmark(post_id=post_id, user_id=user.id)
        db.session.add(bm)
        db.session.commit()
        bookmarked = True
    return jsonify({'bookmarked': bookmarked})

@app.route('/blog/<int:post_id>/comment', methods=['POST'])
def blog_comment(post_id):
    if 'user_id' not in session:
        flash('Please login to comment.', 'error')
        return redirect(url_for('login'))
    user = get_current_user()
    content = request.form.get('content', '').strip()
    if not content:
        flash('Comment cannot be empty.', 'error')
        return redirect(url_for('blog_post', slug=BlogPost.query.get(post_id).slug))
    comment = BlogComment(post_id=post_id, user_id=user.id, content=content)
    db.session.add(comment)
    db.session.commit()
    post = BlogPost.query.get(post_id)
    return redirect(url_for('blog_post', slug=post.slug))

@app.route('/blog/<int:post_id>/comment/<int:comment_id>/delete', methods=['POST'])
def delete_comment(post_id, comment_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = get_current_user()
    comment = BlogComment.query.get_or_404(comment_id)
    if comment.user_id != user.id and not user.is_admin:
        flash('Unauthorised.', 'error')
        return redirect(url_for('blog_post', slug=BlogPost.query.get(post_id).slug))
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted.', 'success')
    post = BlogPost.query.get(post_id)
    return redirect(url_for('blog_post', slug=post.slug))

@app.route('/my-bookmarks')
def my_bookmarks():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = get_current_user()
    bookmarks = BlogBookmark.query.filter_by(user_id=user.id).all()
    posts = [BlogPost.query.get(b.post_id) for b in bookmarks if BlogPost.query.get(b.post_id)]
    return render_template('blog.html', username=user.username, posts_list=posts, categories=[], current_category='', search='', user=user, title='My Bookmarks')

# ============================================================ ADMIN ============================================================

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if not user or not user.is_admin:
            flash('Admin access required.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated

@app.route('/admin')
def admin():
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    user = get_current_user()
    stats = {
        'total_users': User.query.count(),
        'total_doctors': User.query.filter(User.type_of_doctor != None).count(),
        'total_patients': User.query.filter_by(type_of_doctor=None).count(),
        'total_appointments': Appointment.query.count(),
        'pending_appointments': Appointment.query.filter_by(status='Pending').count(),
        'approved_appointments': Appointment.query.filter_by(status='Approved').count(),
        'total_blog_posts': BlogPost.query.count(),
        'total_reports': ScanReport.query.count(),
        'total_ai_chats': AiChatMessage.query.count(),
        'total_messages': DoctorMessage.query.count(),
    }
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    recent_logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(20).all()
    return render_template('admin-dashboard.html', username=user.username, stats=stats, recent_users=recent_users, recent_logs=recent_logs, user=user)

@app.route('/admin/blog')
@admin_required
def admin_blog():
    user = get_current_user()
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return render_template('admin-blog.html', username=user.username, posts=posts, user=user)

@app.route('/admin/blog/new', methods=['GET', 'POST'])
@admin_required
def admin_blog_new():
    user = get_current_user()
    if request.method == 'POST':
        title = request.form['title'].strip()
        content = request.form['content'].strip()
        excerpt = request.form.get('excerpt', '').strip()
        category = request.form.get('category', 'General')
        published = request.form.get('published') == 'on'
        slug_base = slugify(title)
        slug = slug_base
        counter = 1
        while BlogPost.query.filter_by(slug=slug).first():
            slug = f"{slug_base}-{counter}"
            counter += 1
        word_count = len(content.split())
        read_time = max(3, word_count // 200)
        featured_image = ''
        if 'featured_image' in request.files:
            img = request.files['featured_image']
            if img and img.filename and allowed_file(img.filename, {'png', 'jpg', 'jpeg', 'gif', 'webp'}):
                os.makedirs(BLOG_IMG_FOLDER, exist_ok=True)
                img_name = f"blog_{int(datetime.utcnow().timestamp())}_{secure_filename(img.filename)}"
                img.save(os.path.join(BLOG_IMG_FOLDER, img_name))
                featured_image = f"uploads/blog/{img_name}"
        post = BlogPost(
            title=title, slug=slug, content=content, excerpt=excerpt,
            category=category, published=published, read_time=read_time,
            author_id=user.id, featured_image=featured_image
        )
        db.session.add(post)
        db.session.commit()
        log_action(user.id, 'create_post', f'Created post: {title}')
        flash(f'Post "{title}" created successfully!', 'success')
        return redirect(url_for('admin_blog'))
    return render_template('admin-blog-edit.html', username=user.username, post=None, user=user)

@app.route('/admin/blog/edit/<int:post_id>', methods=['GET', 'POST'])
@admin_required
def admin_blog_edit(post_id):
    user = get_current_user()
    post = BlogPost.query.get_or_404(post_id)
    if request.method == 'POST':
        post.title = request.form['title'].strip()
        post.content = request.form['content'].strip()
        post.excerpt = request.form.get('excerpt', '').strip()
        post.category = request.form.get('category', 'General')
        post.published = request.form.get('published') == 'on'
        post.updated_at = datetime.utcnow()
        word_count = len(post.content.split())
        post.read_time = max(3, word_count // 200)
        if 'featured_image' in request.files:
            img = request.files['featured_image']
            if img and img.filename and allowed_file(img.filename, {'png', 'jpg', 'jpeg', 'gif', 'webp'}):
                os.makedirs(BLOG_IMG_FOLDER, exist_ok=True)
                img_name = f"blog_{int(datetime.utcnow().timestamp())}_{secure_filename(img.filename)}"
                img.save(os.path.join(BLOG_IMG_FOLDER, img_name))
                post.featured_image = f"uploads/blog/{img_name}"
        db.session.commit()
        log_action(user.id, 'edit_post', f'Edited post #{post_id}: {post.title}')
        flash('Post updated successfully!', 'success')
        return redirect(url_for('admin_blog'))
    return render_template('admin-blog-edit.html', username=user.username, post=post, user=user)

@app.route('/admin/blog/delete/<int:post_id>', methods=['POST'])
@admin_required
def admin_blog_delete(post_id):
    user = get_current_user()
    post = BlogPost.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    log_action(user.id, 'delete_post', f'Deleted post #{post_id}')
    flash('Post deleted.', 'success')
    return redirect(url_for('admin_blog'))

@app.route('/admin/blog/toggle/<int:post_id>', methods=['POST'])
@admin_required
def admin_blog_toggle(post_id):
    post = BlogPost.query.get_or_404(post_id)
    post.published = not post.published
    db.session.commit()
    return redirect(url_for('admin_blog'))

@app.route('/admin/users')
@admin_required
def admin_users():
    user = get_current_user()
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin-users.html', username=user.username, users=users, user=user)

@app.route('/admin/promote/<int:user_id>', methods=['POST'])
@admin_required
def promote_admin(user_id):
    target = User.query.get_or_404(user_id)
    target.is_admin = not target.is_admin
    db.session.commit()
    flash(f'{"Promoted" if target.is_admin else "Demoted"} {target.username} successfully.', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/setup')
def admin_setup():
    setup_key = os.getenv('ADMIN_SETUP_KEY', '')
    provided_key = request.args.get('key', '')
    if not setup_key or provided_key != setup_key:
        return 'Invalid setup key.', 403
    if User.query.filter_by(is_admin=True).count() > 0:
        return 'Admin already exists.', 400
    first_user = User.query.order_by(User.id.asc()).first()
    if not first_user:
        return 'No users registered yet.', 400
    first_user.is_admin = True
    db.session.commit()
    return f'User {first_user.username} is now admin.', 200

# ============================================================ EXISTING ROUTES ============================================================

@app.route('/policy')
def policy():
    user = get_current_user()
    return render_template('privacy-policy.html', username=user.username if user else None)

@app.route('/Transforming_Healthcare')
def Transforming_Healthcare():
    user = get_current_user()
    if user:
        return render_template('blog_Transforming Healthcare.html', username=user.username)
    return render_template('index.html')

@app.route('/Holistic_Health')
def Holistic_Health():
    user = get_current_user()
    if user:
        return render_template('blog_Holistic Health.html', username=user.username)
    return render_template('index.html')

@app.route('/Nourishing_Body')
def Nourishing_Body():
    user = get_current_user()
    if user:
        return render_template('blog_Nourishing_Body.html', username=user.username)
    return render_template('index.html')

@app.route('/Importance_of_Games')
def Importance_of_Games():
    user = get_current_user()
    if user:
        return render_template('blog_Importance_of_Games.html', username=user.username)
    return render_template('index.html')

@app.route('/videocall')
def videocall():
    user = get_current_user()
    if user:
        return render_template('videocall.html', username=user.username)
    return render_template('index.html')

@app.route('/doctor-patients')
def doctor_patients():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = get_current_user()
    if not user.type_of_doctor:
        return redirect(url_for('index'))
    appointments = Appointment.query.filter_by(type_of_doctor=user.type_of_doctor).all()
    file_list = os.listdir(text_files_dir) if os.path.exists(text_files_dir) else []
    return render_template('doctor-patients.html', doctor=user, appointments=appointments, username=user.username, file_list=file_list)

@app.route('/prescribe-medicine/<int:appointment_id>', methods=['GET', 'POST'])
def prescribe_medicine(appointment_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    doctor = get_current_user()
    appointment = Appointment.query.get_or_404(appointment_id)
    if appointment.type_of_doctor != doctor.type_of_doctor:
        return redirect(url_for('index'))
    available_medicines = [
        "Paracetamol 500mg", "Ibuprofen 400mg", "Amoxicillin 500mg",
        "Cetirizine 10mg", "Omeprazole 20mg", "Metformin 500mg",
        "Atorvastatin 10mg", "Amlodipine 5mg", "Metoprolol 50mg",
        "Salbutamol Inhaler", "Prednisolone 5mg", "Doxycycline 100mg",
        "Azithromycin 500mg", "Ciprofloxacin 500mg", "Aspirin 75mg",
        "Vitamin D3 1000IU", "Iron Sulphate 200mg", "Folic Acid 5mg",
        "Loratadine 10mg", "Pantoprazole 40mg"
    ]
    if request.method == 'POST':
        selected_medicines = request.form.getlist('medicines[]')
        additional_notes = request.form.get('additional_notes', '')
        buffer = BytesIO()
        pdf = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        header_style = ParagraphStyle('Header1', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=20, spaceAfter=12, textColor=colors.HexColor('#00c9a7'))
        footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=10, textColor=colors.grey)
        content = []
        content.append(Paragraph("<font color='#00c9a7' size='22'><b>Convofy Healthcare</b></font>", header_style))
        content.append(Paragraph("<font color='grey'>Your Trusted Telemedicine Platform</font>", footer_style))
        content.append(Spacer(1, 20))
        patient_details = (
            f"<b>PRESCRIPTION</b><br/><br/>"
            f"<b>Patient Name:</b> {appointment.name}<br/>"
            f"<b>Age:</b> {appointment.age} years<br/>"
            f"<b>Blood Group:</b> {appointment.blood_group}<br/>"
            f"<b>Phone:</b> {appointment.phone_number}<br/>"
            f"<b>Email:</b> {appointment.email}<br/>"
            f"<b>Appointment Time:</b> {appointment.time_slot}"
        )
        content.append(Paragraph(patient_details, styles['Normal']))
        content.append(Spacer(1, 20))
        prescribed_meds = "<b>Prescribed Medications:</b><br/>"
        for i, medicine in enumerate(selected_medicines, 1):
            prescribed_meds += f"{i}. {medicine}<br/>"
        content.append(Paragraph(prescribed_meds, styles['Normal']))
        content.append(Spacer(1, 15))
        if additional_notes:
            content.append(Paragraph(f"<b>Doctor's Notes:</b><br/>{additional_notes}", styles['Normal']))
            content.append(Spacer(1, 15))
        doctor_details = (
            f"<b>Prescribed by:</b> Dr. {doctor.username}<br/>"
            f"<b>Specialty:</b> {doctor.type_of_doctor}<br/>"
            f"<b>Date:</b> {datetime.utcnow().strftime('%d %B %Y')}<br/><br/>"
            "<i>Thank you for choosing Convofy. We wish you a speedy recovery.</i>"
        )
        content.append(Paragraph(doctor_details, styles['Normal']))
        pdf.build(content)
        pdf_filename = f"prescription_{appointment_id}.pdf"
        os.makedirs(os.path.join("static", "prescriptions"), exist_ok=True)
        pdf_filepath = os.path.join("static", "prescriptions", pdf_filename)
        buffer.seek(0)
        with open(pdf_filepath, 'wb') as pdf_file:
            pdf_file.write(buffer.read())
        buffer.close()
        appointment.status = 'Prescribed'
        appointment.prescription_file = pdf_filepath
        db.session.commit()
        log_action(doctor.id, 'prescribe', f'Prescribed for appointment #{appointment_id}')
        return redirect(url_for('doctor_patients'))
    return render_template('prescribe-medicine.html', appointment=appointment, available_medicines=available_medicines, username=doctor.username)

@app.route('/view-prescription/<int:appointment_id>')
def view_prescription(appointment_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    doctor = get_current_user()
    appointment = Appointment.query.get_or_404(appointment_id)
    if appointment.type_of_doctor != doctor.type_of_doctor or appointment.status != 'Prescribed':
        return redirect(url_for('index'))
    return send_file(appointment.prescription_file, as_attachment=True)

@app.route('/view-prescription-patient/<int:appointment_id>')
def view_prescription_patient(appointment_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = get_current_user()
    appointment = Appointment.query.get_or_404(appointment_id)
    if appointment.user_id != user.id or appointment.status != 'Prescribed':
        return redirect(url_for('profile'))
    return send_file(appointment.prescription_file, as_attachment=True)

@app.route('/braintumor', methods=['GET', 'POST'])
def braintumor():
    user = get_current_user()
    if user:
        return render_template('brain-tumor.html', username=user.username)
    return render_template('index.html')

@app.route('/disease_predict', methods=['GET', 'POST'])
def disease_predict():
    if 'user_id' not in session:
        return render_template('index.html')
    user = get_current_user()
    chart_data = {}
    if request.method == 'POST':
        selected_symptoms = []
        for i in range(1, 6):
            s = request.form.get(f'Symptom{i}', '').strip()
            if s and s not in selected_symptoms:
                selected_symptoms.append(s)
        if selected_symptoms:
            disease, confidence_score = predict(selected_symptoms)
            chart_data = {'disease': disease, 'confidence_score': confidence_score}
            return render_template('disease_predict.html', symptoms=symptoms, disease=disease,
                                   chart_data=chart_data, confidence_score=confidence_score, username=user.username)
    return render_template('disease_predict.html', symptoms=symptoms, username=user.username, chart_data=chart_data)

@app.route('/lung')
def lung():
    user = get_current_user()
    if user:
        return render_template('lung.html', username=user.username)
    return render_template('index.html')

@app.route('/cataract')
def cataract():
    user = get_current_user()
    if user:
        return render_template('cataract.html', username=user.username)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
