#!/usr/bin/env python3
"""
SmartEdu AI Application Runner
Development server with auto-reload and debugging features
"""

import os
import sys
from app import app, db

def main():
    """Main entry point for the application"""
    
    # Set environment variables
    os.environ.setdefault('FLASK_ENV', 'development')
    
    # Create required directories
    create_directories()
    
    # Initialize database if needed
    if not os.path.exists('smartedu_dev.db') and os.environ.get('DATABASE_URL', '').endswith('smartedu_dev.db'):
        print("Initializing development database...")
        from init_db import init_database
        init_database()
    
    # Run the application
    print("🚀 Starting SmartEdu AI Development Server...")
    print("📍 Access the application at: http://localhost:5000")
    print("👤 Demo Login: admin/123456, teacher/123456, student/123456")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=True,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n👋 SmartEdu AI server stopped gracefully")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

def create_directories():
    """Create necessary directories for the application"""
    
    directories = [
        'static/uploads',
        'models',
        'backups',
        'logs'
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"📁 Created directory: {directory}")

def check_dependencies():
    """Check if all required dependencies are installed"""
    
    required_packages = [
        'flask',
        'flask_sqlalchemy',
        'opencv-python',
        'face_recognition',
        'scikit-learn',
        'pandas',
        'numpy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Install with: pip install -r requirements.txt")
        sys.exit(1)
    else:
        print("✅ All dependencies are installed")

def check_database():
    """Check database connectivity"""
    
    try:
        with app.app_context():
            db.engine.execute('SELECT 1')
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\n💡 Make sure MySQL is running and the database exists")
        sys.exit(1)

if __name__ == '__main__':
    print("🎓 SmartEdu AI - Student Performance Prediction System")
    print("=" * 50)
    
    # Perform system checks
    check_dependencies()
    check_database()
    
    # Start the application
    main()
