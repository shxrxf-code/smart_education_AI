#!/usr/bin/env python3
"""
Sample Data Creation for SmartEdu AI
Creates sample data for testing the application
"""

import sys
import os
from datetime import datetime, date
from werkzeug.security import generate_password_hash

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app_simple import app, db, User, Student, Teacher, Subject, Attendance, AcademicRecord, PerformancePrediction

def create_sample_data():
    """Create sample data for testing"""
    
    with app.app_context():
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
        print("\nDatabase is now ready with sample data.")
        print("You can now login with:")
        print("Admin: admin / 123456")
        print("Teacher: teacher / 123456")
        print("Student: student / 123456")

if __name__ == '__main__':
    try:
        create_sample_data()
    except Exception as e:
        print(f"Error creating sample data: {e}")
        sys.exit(1)
