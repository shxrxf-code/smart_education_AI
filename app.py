from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import cv2
import numpy as np
import face_recognition
from sqlalchemy import func
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error
import pickle
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/smartedu'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False)  # 'student', 'teacher', 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    student_profile = db.relationship('Student', backref='user', uselist=False)
    teacher_profile = db.relationship('Teacher', backref='user', uselist=False)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    enrollment_date = db.Column(db.Date, default=datetime.utcnow().date())
    face_image_path = db.Column(db.String(255))
    
    # Relationships
    attendance_records = db.relationship('Attendance', backref='student', lazy=True)
    academic_records = db.relationship('AcademicRecord', backref='student', lazy=True)
    predictions = db.relationship('PerformancePrediction', backref='student', lazy=True)

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    teacher_id = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    department = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text)
    credits = db.Column(db.Integer, default=3)
    
    # Relationships
    academic_records = db.relationship('AcademicRecord', backref='subject', lazy=True)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(10), nullable=False)  # 'present', 'absent', 'late'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    recognition_confidence = db.Column(db.Float)

class AcademicRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    semester = db.Column(db.String(20), nullable=False)
    assessment_type = db.Column(db.String(50), nullable=False)  # 'exam', 'assignment', 'quiz', 'project'
    score = db.Column(db.Float, nullable=False)
    max_score = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    remarks = db.Column(db.Text)

class PerformancePrediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    prediction_date = db.Column(db.DateTime, default=datetime.utcnow)
    semester = db.Column(db.String(20), nullable=False)
    
    # Predictions
    gpa_prediction = db.Column(db.Float)
    failure_risk = db.Column(db.Float)  # 0-1 probability
    dropout_risk = db.Column(db.Float)  # 0-1 probability
    
    # Feature importance
    attendance_impact = db.Column(db.Float)
    previous_performance_impact = db.Column(db.Float)
    
    # Recommendations
    recommendations = db.Column(db.Text)
    weak_subjects = db.Column(db.Text)  # JSON string

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Face Recognition Module
class FaceRecognitionSystem:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_ids = []
        self.load_known_faces()
    
    def load_known_faces(self):
        students = Student.query.filter(Student.face_image_path.isnot(None)).all()
        for student in students:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], student.face_image_path)
            if os.path.exists(image_path):
                image = face_recognition.load_image_file(image_path)
                encodings = face_recognition.face_encodings(image)
                if encodings:
                    self.known_face_encodings.append(encodings[0])
                    self.known_face_ids.append(student.id)
    
    def recognize_face(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        recognized_students = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            
            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index] and face_distances[best_match_index] < 0.6:
                    student_id = self.known_face_ids[best_match_index]
                    confidence = 1 - face_distances[best_match_index]
                    recognized_students.append({'student_id': student_id, 'confidence': confidence})
        
        return recognized_students

# ML Prediction Module
class PerformancePredictor:
    def __init__(self):
        self.gpa_model = None
        self.risk_model = None
        self.dropout_model = None
        self.load_models()
    
    def load_models(self):
        try:
            with open('models/gpa_model.pkl', 'rb') as f:
                self.gpa_model = pickle.load(f)
            with open('models/risk_model.pkl', 'rb') as f:
                self.risk_model = pickle.load(f)
            with open('models/dropout_model.pkl', 'rb') as f:
                self.dropout_model = pickle.load(f)
        except FileNotFoundError:
            self.train_models()
    
    def extract_features(self, student_id, semester):
        student = Student.query.get(student_id)
        
        # Attendance features
        attendance_records = Attendance.query.filter_by(student_id=student_id).all()
        attendance_rate = len([r for r in attendance_records if r.status == 'present']) / len(attendance_records) if attendance_records else 0
        
        # Academic features
        academic_records = AcademicRecord.query.filter_by(student_id=student_id).all()
        if academic_records:
            avg_score = sum(r.score / r.max_score for r in academic_records) / len(academic_records)
            subject_scores = {}
            for record in academic_records:
                subject_name = record.subject.name
                if subject_name not in subject_scores:
                    subject_scores[subject_name] = []
                subject_scores[subject_name].append(record.score / record.max_score)
            
            # Subject-wise averages
            subject_averages = {subj: sum(scores) / len(scores) for subj, scores in subject_scores.items()}
        else:
            avg_score = 0
            subject_averages = {}
        
        # Temporal features
        current_date = datetime.utcnow().date()
        enrollment_duration = (current_date - student.enrollment_date).days
        
        features = {
            'attendance_rate': attendance_rate,
            'avg_score': avg_score,
            'enrollment_duration': enrollment_duration,
            'num_subjects': len(subject_averages),
            'score_variance': np.var(list(subject_averages.values())) if subject_averages else 0
        }
        
        return features
    
    def predict_performance(self, student_id, semester):
        features = self.extract_features(student_id, semester)
        feature_vector = np.array([list(features.values())]).reshape(1, -1)
        
        # Make predictions
        gpa_pred = self.gpa_model.predict(feature_vector)[0] if self.gpa_model else 2.0
        failure_risk = self.risk_model.predict_proba(feature_vector)[0][1] if self.risk_model else 0.1
        dropout_risk = self.dropout_model.predict_proba(feature_vector)[0][1] if self.dropout_model else 0.05
        
        # Generate recommendations
        recommendations = self.generate_recommendations(features, failure_risk, dropout_risk)
        weak_subjects = self.identify_weak_subjects(student_id)
        
        return {
            'gpa_prediction': round(gpa_pred, 2),
            'failure_risk': round(failure_risk, 3),
            'dropout_risk': round(dropout_risk, 3),
            'attendance_impact': features['attendance_rate'],
            'previous_performance_impact': features['avg_score'],
            'recommendations': recommendations,
            'weak_subjects': json.dumps(weak_subjects)
        }
    
    def generate_recommendations(self, features, failure_risk, dropout_risk):
        recommendations = []
        
        if features['attendance_rate'] < 0.8:
            recommendations.append("Improve attendance rate - attend classes regularly")
        
        if features['avg_score'] < 0.6:
            recommendations.append("Focus on improving academic performance - seek additional help")
        
        if failure_risk > 0.7:
            recommendations.append("High failure risk detected - immediate intervention required")
        
        if dropout_risk > 0.5:
            recommendations.append("Consider counseling services to address challenges")
        
        if features['score_variance'] > 0.3:
            recommendations.append("Inconsistent performance across subjects - focus on weak areas")
        
        return "; ".join(recommendations) if recommendations else "Continue current performance"
    
    def identify_weak_subjects(self, student_id):
        academic_records = AcademicRecord.query.filter_by(student_id=student_id).all()
        subject_scores = {}
        
        for record in academic_records:
            subject_name = record.subject.name
            if subject_name not in subject_scores:
                subject_scores[subject_name] = []
            subject_scores[subject_name].append(record.score / record.max_score)
        
        weak_subjects = []
        for subject, scores in subject_scores.items():
            avg_score = sum(scores) / len(scores)
            if avg_score < 0.6:  # Below 60%
                weak_subjects.append({'subject': subject, 'avg_score': avg_score})
        
        return weak_subjects
    
    def train_models(self):
        # This would be implemented with historical data
        # For now, create dummy models
        from sklearn.dummy import DummyClassifier, DummyRegressor
        
        self.gpa_model = DummyRegressor(strategy="mean")
        self.risk_model = DummyClassifier(strategy="prior")
        self.dropout_model = DummyClassifier(strategy="prior")
        
        # Save models
        os.makedirs('models', exist_ok=True)
        with open('models/gpa_model.pkl', 'wb') as f:
            pickle.dump(self.gpa_model, f)
        with open('models/risk_model.pkl', 'wb') as f:
            pickle.dump(self.risk_model, f)
        with open('models/dropout_model.pkl', 'wb') as f:
            pickle.dump(self.dropout_model, f)

# Initialize systems
face_rec_system = FaceRecognitionSystem()
performance_predictor = PerformancePredictor()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'student':
        return render_template('student_dashboard.html')
    elif current_user.role == 'teacher':
        return render_template('teacher_dashboard.html')
    else:
        return render_template('admin_dashboard.html')

@app.route('/attendance')
@login_required
def attendance():
    if current_user.role == 'teacher':
        subjects = Subject.query.all()
        return render_template('attendance.html', subjects=subjects)
    else:
        return redirect(url_for('dashboard'))

@app.route('/api/mark_attendance', methods=['POST'])
@login_required
def mark_attendance():
    subject_id = request.form.get('subject_id')
    
    # Process face recognition from uploaded image or camera feed
    # This is a simplified version
    students_present = []
    
    date = datetime.utcnow().date()
    
    for student_data in students_present:
        attendance = Attendance(
            student_id=student_data['student_id'],
            subject_id=subject_id,
            date=date,
            status='present',
            recognition_confidence=student_data['confidence']
        )
        db.session.add(attendance)
    
    db.session.commit()
    return jsonify({'status': 'success', 'students_marked': len(students_present)})

@app.route('/api/predict_performance/<int:student_id>')
@login_required
def predict_performance(student_id):
    semester = request.args.get('semester', 'current')
    prediction = performance_predictor.predict_performance(student_id, semester)
    
    # Save prediction to database
    perf_pred = PerformancePrediction(
        student_id=student_id,
        semester=semester,
        **prediction
    )
    db.session.add(perf_pred)
    db.session.commit()
    
    return jsonify(prediction)

@app.route('/analytics')
@login_required
def analytics():
    if current_user.role in ['teacher', 'admin']:
        return render_template('analytics.html')
    else:
        return redirect(url_for('dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
