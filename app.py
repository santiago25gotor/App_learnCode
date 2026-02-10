"""
Aplicación Flask principal - Python Learning Platform
"""
from flask import Flask, render_template, session, redirect, url_for
from flask_cors import CORS
from config import Config
from backend.routes import api
import os


def create_app():
    """Factory para crear la aplicación Flask"""
    
    # Crear instancia de Flask
    app = Flask(__name__)
    
    # Configuración
    app.config.from_object(Config)
    
    # Habilitar CORS
    CORS(app, origins=Config.CORS_ORIGINS, supports_credentials=True)
    
    # Registrar blueprints (rutas de la API)
    app.register_blueprint(api)
    
    # ============================================
    # RUTAS DEL FRONTEND (PÁGINAS HTML)
    # ============================================
    
    @app.route('/')
    def index():
        """Página principal - Landing page"""
        if 'user_id' in session:
            return redirect(url_for('course'))
        return render_template('index_new.html')
    
    @app.route('/login')
    def login_page():
        """Página de login"""
        if 'user_id' in session:
            return redirect(url_for('course'))
        return render_template('login_new.html')
    
    @app.route('/register')
    def register_page():
        """Página de registro - redirige a login (modo integrado)"""
        return redirect(url_for('login_page'))
    
    @app.route('/course')
    def course():
        """Página del curso (requiere autenticación)"""
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        return render_template('course_new.html', username=session.get('username'))
    
    @app.route('/lesson/<lesson_id>')
    def lesson_detail(lesson_id):
        """Página de detalle de lección"""
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        return render_template('lesson_new.html', lesson_id=lesson_id)
    
    @app.route('/exam/<category>')
    def exam_page(category):
        """Página de examen por categoría"""
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        return render_template('exam.html', category=category)
    
    @app.route('/profile')
    def profile_page():
        """Página de perfil de usuario"""
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        return render_template('profile.html')
    
    @app.route('/placement-test')
    def placement_test_page():
        """Página de test de nivel inicial"""
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        return render_template('placement_test.html')
    
    # ============================================
    # MANEJADORES DE ERRORES
    # ============================================
    
    @app.errorhandler(404)
    def not_found(error):
        """Página de error 404"""
        return render_template('404_new.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Página de error 500"""
        return render_template('500_new.html'), 500
    
    return app


if __name__ == '__main__':
    # Crear aplicación
    app = create_app()
    
    # Ejecutar servidor
    print("\n" + "="*60)
    print("Python Learning Platform - Servidor iniciado")
    print("="*60)
    print(f"URL: http://127.0.0.1:5000")
    print(f"Modo: {'Desarrollo' if Config.DEBUG else 'Produccion'}")
    print("="*60 + "\n")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=Config.DEBUG
    )