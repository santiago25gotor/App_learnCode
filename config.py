import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    """Configuración general de la aplicación"""
    
    # Flask
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_ENV', 'development') == 'development'
    
    # Firebase
    FIREBASE_CREDENTIALS = os.getenv('FIREBASE_CREDENTIALS_PATH', 'firebase-credentials.json')
    FIREBASE_WEB_API_KEY = os.getenv('FIREBASE_WEB_API_KEY', 'AIzaSyBdz1cyFzEcg1MHYp0FT6WXiVEZKbtg2Ds')
    
    # Colecciones Firestore
    USERS_COLLECTION = 'users'
    LESSONS_COLLECTION = 'lessons'
    PROGRESS_COLLECTION = 'user_progress'
    
    # Configuración del curso
    LESSON_CATEGORIES = ['Python Básico', 'Python Intermedio', 'Python Avanzado']
    
    # CORS
    CORS_ORIGINS = ['http://localhost:5000', 'http://127.0.0.1:5000']