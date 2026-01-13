#!/usr/bin/env python3
"""
Database Initialization Script for SmartEdu AI
This script creates the database schema and inserts initial data
"""

import sys
import os
from datetime import datetime, date
from werkzeug.security import generate_password_hash

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app_simple import app, db, User, Student, Teacher, Subject

def init_database():
    """Initialize the database with tables and sample data"""
    
    with app.app_context():
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        print("Tables created successfully!")
        
        # Clear existing data (for fresh start)
        print("Clearing existing data...")
        User.query.delete()
        Student.query.delete()
        Teacher.query.delete()
        Subject.query.delete()
        db.session.commit()
        
        # Create sample users
        print("Creating sample users...")
        
        # Admin user
        admin = User(
            username='admin',
            email='admin@smartedu.ai',
            password_hash=generate_password_hash('123456'),
            role='admin'
        )
        db.session.add(admin)
        
        # Teacher users
        teacher1 = User(
            username='teacher',
            email='teacher@smartedu.ai',
            password_hash=generate_password_hash('123456'),
            role='teacher'
        )
        db.session.add(teacher1)
        
        teacher2 = User(
            username='professor',
            email='professor@smartedu.ai',
            password_hash=generate_password_hash('123456'),
            role='teacher'
        )
        db.session.add(teacher2)
        
        # Student users
        student1 = User(
            username='student',
            email='student@smartedu.ai',
            password_hash=generate_password_hash('123456'),
            role='student'
        )
        db.session.add(student1)
        
        student2 = User(
            username='john_doe',
            email='john.doe@smartedu.ai',
            password_hash=generate_password_hash('123456'),
            role='student'
        )
        db.session.add(student2)
        
        student3 = User(
            username='jane_smith',
            email='jane.smith@smartedu.ai',
            password_hash=generate_password_hash('123456'),
            role='student'
        )
        db.session.add(student3)
        
        db.session.commit()
        
        # Create teacher profiles
        print("Creating teacher profiles...")
        
        teacher_profile1 = Teacher(
            user_id=teacher1.id,
            teacher_id='TCH001',
            first_name='Robert',
            last_name='Johnson',
            department='Computer Science',
            phone='555-0101',
            email='robert.johnson@smartedu.ai'
        )
        db.session.add(teacher_profile1)
        
        teacher_profile2 = Teacher(
            user_id=teacher2.id,
            teacher_id='TCH002',
            first_name='Sarah',
            last_name='Williams',
            department='Mathematics',
            phone='555-0102',
            email='sarah.williams@smartedu.ai'
        )
        db.session.add(teacher_profile2)
        
        db.session.commit()
        
        # Create student profiles
        print("Creating student profiles...")
        
        student_profile1 = Student(
            user_id=student1.id,
            student_id='STU001',
            first_name='Alice',
            last_name='Anderson',
            date_of_birth=date(2002, 5, 15),
            gender='Female',
            phone='555-0201',
            address='123 Main St, City, State',
            enrollment_date=date(2021, 8, 15)
        )
        db.session.add(student_profile1)
        
        student_profile2 = Student(
            user_id=student2.id,
            student_id='STU002',
            first_name='John',
            last_name='Doe',
            date_of_birth=date(2003, 3, 22),
            gender='Male',
            phone='555-0202',
            address='456 Oak Ave, City, State',
            enrollment_date=date(2021, 8, 15)
        )
        db.session.add(student_profile2)
        
        student_profile3 = Student(
            user_id=student3.id,
            student_id='STU003',
            first_name='Jane',
            last_name='Smith',
            date_of_birth=date(2002, 11, 8),
            gender='Female',
            phone='555-0203',
            address='789 Pine Rd, City, State',
            enrollment_date=date(2021, 8, 15)
        )
        db.session.add(student_profile3)
        
        db.session.commit()
        
        # Create subjects
        print("Creating subjects...")
        
        subjects = [
            Subject(name='Mathematics', code='MATH101', description='Calculus and Linear Algebra', credits=4),
            Subject(name='Physics', code='PHYS101', description='Introduction to Physics', credits=4),
            Subject(name='Chemistry', code='CHEM101', description='General Chemistry', credits=3),
            Subject(name='Computer Science', code='CS101', description='Introduction to Programming', credits=4),
            Subject(name='English', code='ENG101', description='English Literature and Composition', credits=3),
            Subject(name='History', code='HIST101', description='World History', credits=3),
            Subject(name='Biology', code='BIO101', description='Introduction to Biology', credits=4),
            Subject(name='Economics', code='ECON101', description='Microeconomics', credits=3)
        ]
        
        for subject in subjects:
            db.session.add(subject)
        
        db.session.commit()
        
        print("Database initialization completed successfully!")
        print("\nSample Login Credentials:")
        print("Admin: admin / 123456")
        print("Teacher: teacher / 123456")
        print("Student: student / 123456")

def create_sample_data():
    """Create additional sample data for testing"""
    
    with app.app_context():
        from app import Attendance, AcademicRecord, PerformancePrediction
        
        print("Creating sample attendance records...")
        
        # Sample attendance data
        attendance_records = [
            # Alice Anderson (STU001)
            Attendance(student_id=1, subject_id=1, date=date(2024, 1, 15), status='present', recognition_confidence=0.95),
            Attendance(student_id=1, subject_id=2, date=date(2024, 1, 15), status='present', recognition_confidence=0.92),
            Attendance(student_id=1, subject_id=4, date=date(2024, 1, 16), status='late', recognition_confidence=0.88),
            
            # John Doe (STU002)
            Attendance(student_id=2, subject_id=1, date=date(2024, 1, 15), status='present', recognition_confidence=0.91),
            Attendance(student_id=2, subject_id=2, date=date(2024, 1, 15), status='absent', recognition_confidence=0.0),
            Attendance(student_id=2, subject_id=4, date=date(2024, 1, 16), status='present', recognition_confidence=0.94),
            
            # Jane Smith (STU003)
            Attendance(student_id=3, subject_id=1, date=date(2024, 1, 15), status='present', recognition_confidence=0.96),
            Attendance(student_id=3, subject_id=2, date=date(2024, 1, 15), status='present', recognition_confidence=0.93),
            Attendance(student_id=3, subject_id=4, date=date(2024, 1, 16), status='present', recognition_confidence=0.89),
        ]
        
        for record in attendance_records:
            db.session.add(record)
        
        print("Creating sample academic records...")
        
        # Sample academic data
        academic_records = [
            # Alice Anderson
            AcademicRecord(student_id=1, subject_id=1, semester='Fall 2023', assessment_type='exam', score=85, max_score=100, date=date(2023, 12, 15)),
            AcademicRecord(student_id=1, subject_id=2, semester='Fall 2023', assessment_type='exam', score=92, max_score=100, date=date(2023, 12, 16)),
            AcademicRecord(student_id=1, subject_id=4, semester='Fall 2023', assessment_type='project', score=88, max_score=100, date=date(2023, 12, 10)),
            
            # John Doe
            AcademicRecord(student_id=2, subject_id=1, semester='Fall 2023', assessment_type='exam', score=72, max_score=100, date=date(2023, 12, 15)),
            AcademicRecord(student_id=2, subject_id=2, semester='Fall 2023', assessment_type='exam', score=68, max_score=100, date=date(2023, 12, 16)),
            AcademicRecord(student_id=2, subject_id=4, semester='Fall 2023', assessment_type='project', score=75, max_score=100, date=date(2023, 12, 10)),
            
            # Jane Smith
            AcademicRecord(student_id=3, subject_id=1, semester='Fall 2023', assessment_type='exam', score=95, max_score=100, date=date(2023, 12, 15)),
            AcademicRecord(student_id=3, subject_id=2, semester='Fall 2023', assessment_type='exam', score=89, max_score=100, date=date(2023, 12, 16)),
            AcademicRecord(student_id=3, subject_id=4, semester='Fall 2023', assessment_type='project', score=93, max_score=100, date=date(2023, 12, 10)),
        ]
        
        for record in academic_records:
            db.session.add(record)
        
        print("Creating sample performance predictions...")
        
        # Sample prediction data
        predictions = [
            PerformancePrediction(
                student_id=1, semester='Spring 2024',
                gpa_prediction=3.8, failure_risk=0.05, dropout_risk=0.02,
                attendance_impact=0.92, previous_performance_impact=0.88,
                recommendations='Continue excellent performance. Consider advanced courses.',
                weak_subjects='[]'
            ),
            PerformancePrediction(
                student_id=2, semester='Spring 2024',
                gpa_prediction=2.4, failure_risk=0.35, dropout_risk=0.15,
                attendance_impact=0.65, previous_performance_impact=0.72,
                recommendations='Focus on improving attendance and seek help in Mathematics.',
                weak_subjects='[{"subject": "Mathematics", "avg_score": 0.72}]'
            ),
            PerformancePrediction(
                student_id=3, semester='Spring 2024',
                gpa_prediction=3.6, failure_risk=0.08, dropout_risk=0.03,
                attendance_impact=0.95, previous_performance_impact=0.92,
                recommendations='Maintain current performance. Excellent candidate for honors program.',
                weak_subjects='[]'
            ),
        ]
        
        for prediction in predictions:
            db.session.add(prediction)
        
        db.session.commit()
        
        print("Sample data created successfully!")

if __name__ == '__main__':
    try:
        init_database()
        
        # Ask if user wants to create sample data
        create_sample = input("\nDo you want to create sample data? (y/n): ").lower().strip()
        if create_sample in ['y', 'yes']:
            create_sample_data()
        
        print("\nDatabase setup completed!")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)
