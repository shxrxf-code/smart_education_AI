from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from sqlalchemy import func
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error
import pickle
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smartedu_dev.db'
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

# Simplified Face Recognition System (placeholder)
class FaceRecognitionSystem:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_ids = []
        self.load_known_faces()
    
    def load_known_faces(self):
        # Placeholder implementation
        pass
    
    def recognize_face(self, frame):
        # Placeholder implementation - returns mock data
        return [
            {'student_id': 1, 'confidence': 0.95},
            {'student_id': 2, 'confidence': 0.87}
        ]

# Simplified ML Prediction Module
class PerformancePredictor:
    def __init__(self):
        self.gpa_model = None
        self.risk_model = None
        self.dropout_model = None
        self.load_models()
    
    def load_models(self):
        # Create simple dummy models for demo
        from sklearn.dummy import DummyRegressor, DummyClassifier
        
        self.gpa_model = DummyRegressor(strategy="mean")
        self.risk_model = DummyClassifier(strategy="prior")
        self.dropout_model = DummyClassifier(strategy="prior")
    
    def extract_features(self, student_id, semester):
        # Extract features from database
        student = Student.query.get(student_id)
        
        # Attendance features
        attendance_records = Attendance.query.filter_by(student_id=student_id).all()
        attendance_rate = len([r for r in attendance_records if r.status == 'present']) / len(attendance_records) if attendance_records else 0.8
        
        # Academic features
        academic_records = AcademicRecord.query.filter_by(student_id=student_id).all()
        if academic_records:
            avg_score = sum(r.score / r.max_score for r in academic_records) / len(academic_records)
        else:
            avg_score = 0.75
        
        # Temporal features
        current_date = datetime.utcnow().date()
        enrollment_duration = (current_date - student.enrollment_date).days if student else 365
        
        features = {
            'attendance_rate': attendance_rate,
            'avg_score': avg_score,
            'enrollment_duration': enrollment_duration,
            'num_subjects': 5,
            'score_variance': 0.1
        }
        
        return features
    
    def predict_performance(self, student_id, semester):
        features = self.extract_features(student_id, semester)
        
        # Make simple predictions based on features
        gpa_pred = 2.5 + features['avg_score'] * 1.5 + features['attendance_rate'] * 0.5
        failure_risk = max(0, 1 - features['avg_score'] - features['attendance_rate'] + 0.2)
        dropout_risk = failure_risk * 0.7
        
        # Generate recommendations
        recommendations = self.generate_recommendations(features, failure_risk, dropout_risk)
        weak_subjects = self.identify_weak_subjects(student_id)
        
        return {
            'gpa_prediction': round(min(4.0, gpa_pred), 2),
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
        # Check if it's an AJAX request (JSON expected)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
            try:
                data = request.get_json() if request.is_json else request.form
                username = data.get('username')
                password = data.get('password')
                
                user = User.query.filter_by(username=username).first()
                if user and check_password_hash(user.password_hash, password):
                    login_user(user)
                    return jsonify({
                        'success': True,
                        'message': 'Login successful',
                        'redirect': url_for('dashboard'),
                        'user': {
                            'id': user.id,
                            'username': user.username,
                            'role': user.role
                        }
                    })
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Invalid username or password'
                    }), 401
            except Exception as e:
                print(f'Login error: {e}')
                return jsonify({
                    'success': False,
                    'message': 'An error occurred during login'
                }), 500
        else:
            # Regular form submission
            username = request.form.get('username')
            password = request.form.get('password')
            
            try:
                user = User.query.filter_by(username=username).first()
                if user and check_password_hash(user.password_hash, password):
                    login_user(user)
                    return redirect(url_for('dashboard'))
                else:
                    flash('Invalid username or password')
            except Exception as e:
                print(f'Login error: {e}')
                flash('An error occurred during login')
    
    return render_template('login.html')

@app.route('/api/update_settings', methods=['POST'])
@login_required
def update_settings():
    """Update system settings API"""
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        data = request.get_json()
        # Here you would typically save settings to database or config file
        # For now, just simulate saving
        print(f'Settings updated: {data}')
        
        return jsonify({
            'success': True, 
            'message': 'Settings saved successfully'
        })
    except Exception as e:
        print(f'Settings update error: {e}')
        return jsonify({
            'success': False, 
            'message': 'An error occurred while saving settings'
        }), 500

@app.route('/api/initiate_backup', methods=['POST'])
@login_required
def initiate_backup():
    """Initiate system backup API"""
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        # Here you would typically trigger backup process
        print('Backup process initiated')
        
        return jsonify({
            'success': True, 
            'message': 'Backup process initiated successfully'
        })
    except Exception as e:
        print(f'Backup error: {e}')
        return jsonify({
            'success': False, 
            'message': 'An error occurred during backup'
        }), 500

@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    return render_template('profile.html')

@app.route('/settings')
@login_required
def settings():
    """System settings page"""
    if current_user.role != 'admin':
        return redirect(url_for('dashboard'))
    return render_template('settings.html')

@app.route('/api/update_profile', methods=['POST'])
@login_required
def update_profile():
    """Update user profile API"""
    try:
        data = request.get_json()
        user = User.query.get(current_user.id)
        
        if user:
            user.email = data.get('email', user.email)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Profile updated successfully'})
        else:
            return jsonify({'success': False, 'message': 'User not found'}), 404
    except Exception as e:
        print(f'Profile update error: {e}')
        return jsonify({'success': False, 'message': 'An error occurred'}), 500

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
    
    # Simulate face recognition results
    students_present = face_rec_system.recognize_face(None)
    
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
    app.run(debug=True, host='0.0.0.0', port=5000)
