from flask import Flask, render_template, session, redirect, url_for
from flask_cors import CORS
from config import Config

from backend.api.auth_routes import auth_api
from backend.api.user_routes import user_api
from backend.api.lesson_routes import lesson_api
from backend.api.code_routes import code_api
from backend.api.admin_routes import admin_api   


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, origins=Config.CORS_ORIGINS, supports_credentials=True)

    app.register_blueprint(auth_api,          url_prefix='/api/auth')
    app.register_blueprint(user_api,          url_prefix='/api/user')
    app.register_blueprint(lesson_api,        url_prefix='/api/lessons')
    app.register_blueprint(code_api,          url_prefix='/api/code')
    app.register_blueprint(admin_api,         url_prefix='/api/admin')  # ← NUEVO
  
    @app.route('/')
    def index():
        if 'user_id' in session:
            return redirect(url_for('course'))
        return render_template('index_new.html')

    @app.route('/login')
    def login_page():
        if 'user_id' in session:
            return redirect(url_for('course'))
        return render_template('login_new.html')

    @app.route('/register')
    def register_page():
        return redirect(url_for('login_page'))

    @app.route('/course')
    def course():
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        return render_template('course_new.html', username=session.get('username'))

    @app.route('/lesson/<lesson_id>')
    def lesson_detail(lesson_id):
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        return render_template('lesson_new.html', lesson_id=lesson_id)

    @app.route('/exam/<category>')
    def exam_page(category):
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        return render_template('exam.html', category=category)

    @app.route('/profile')
    def profile_page():
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        return render_template('profile.html')

    @app.route('/placement-test')
    def placement_test_page():
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        return render_template('placement_test.html')

    @app.route('/n8n')
    def n8n_page():
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        return render_template('n8n.html')

    @app.route('/admin')                          # ← NUEVO
    def admin_page():
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        return render_template('admin.html')

    @app.errorhandler(404)
    def not_found(error):
        return render_template('404_new.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('500_new.html'), 500

    return app


if __name__ == '__main__':
    app = create_app()
    print("\n" + "="*60)
    print("Python Learning Platform - Servidor iniciado")
    print("="*60)
    print(f"URL: http://127.0.0.1:5000")
    print(f"Modo: {'Desarrollo' if Config.DEBUG else 'Produccion'}")
    print("="*60 + "\n")
    app.run(host='0.0.0.0', port=5000, debug=Config.DEBUG)
