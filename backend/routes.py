"""
Rutas y endpoints de la API Flask
"""
from flask import Blueprint, request, jsonify, session
from backend.firebase_service import firebase_service
from backend.validators import validate_email, validate_password, validate_username
from functools import wraps

# Crear Blueprint para las rutas de la API
api = Blueprint('api', __name__, url_prefix='/api')


# ============================================
# DECORADOR DE AUTENTICACIÓN
# ============================================

def login_required(f):
    """Decorador para proteger rutas que requieren autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'message': 'Debes iniciar sesión'
            }), 401
        return f(*args, **kwargs)
    return decorated_function


# ============================================
# ENDPOINTS DE AUTENTICACIÓN
# ============================================

@api.route('/register', methods=['POST'])
def register():
    """
    Endpoint de registro de usuario
    
    Body JSON:
        {
            "username": "juan123",
            "email": "juan@example.com",
            "password": "SecurePass123!"
        }
    """
    try:
        data = request.get_json()
        
        # Validar datos recibidos
        if not data:
            return jsonify({
                'success': False,
                'message': 'No se recibieron datos'
            }), 400
        
        username = data.get('username', '').strip().lower()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # Validar username
        is_valid, message = validate_username(username)
        if not is_valid:
            return jsonify({'success': False, 'message': message}), 400
        
        # Validar email
        if not validate_email(email):
            return jsonify({
                'success': False,
                'message': 'Formato de email inválido'
            }), 400
        
        # Validar contraseña
        is_valid, message = validate_password(password)
        if not is_valid:
            return jsonify({'success': False, 'message': message}), 400
        
        # Verificar si el usuario ya existe
        if firebase_service.user_exists(username=username):
            return jsonify({
                'success': False,
                'message': 'El usuario ya existe'
            }), 400
        
        if firebase_service.user_exists(email=email):
            return jsonify({
                'success': False,
                'message': 'El email ya está registrado'
            }), 400
        
        # Crear usuario en Firebase
        success, message, user_id = firebase_service.create_user(email, password, username)
        
        if success:
            # Guardar sesión
            session['user_id'] = user_id
            session['username'] = username
            
            return jsonify({
                'success': True,
                'message': 'Usuario registrado exitosamente',
                'user': {
                    'id': user_id,
                    'username': username,
                    'email': email
                }
            }), 201
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error en el servidor: {str(e)}'
        }), 500


@api.route('/login', methods=['POST'])
def login():
    """
    Endpoint de inicio de sesión
    
    Body JSON:
        {
            "identifier": "juan123 o juan@example.com",
            "password": "SecurePass123!"
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No se recibieron datos'
            }), 400
        
        identifier = data.get('identifier', '').strip().lower()
        password = data.get('password', '')
        
        # Determinar si es email o username
        if '@' in identifier:
            # Es un email
            success, message, user_data = firebase_service.verify_user(identifier, password)
        else:
            # Es un username
            user = firebase_service.get_user_by_username(identifier)
            if user:
                success, message, user_data = firebase_service.verify_user(user['email'], password)
            else:
                return jsonify({
                    'success': False,
                    'message': 'Usuario no encontrado'
                }), 404
        
        if success:
            # Guardar sesión
            session['user_id'] = user_data['uid']
            session['username'] = user_data['username']
            
            return jsonify({
                'success': True,
                'message': 'Login exitoso',
                'user': {
                    'id': user_data['uid'],
                    'username': user_data['username'],
                    'email': user_data['email']
                }
            }), 200
        else:
            return jsonify({'success': False, 'message': message}), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error en el servidor: {str(e)}'
        }), 500


@api.route('/logout', methods=['POST'])
@login_required
def logout():
    """Cerrar sesión"""
    username = session.get('username', 'Usuario')
    session.clear()
    
    return jsonify({
        'success': True,
        'message': f'Hasta luego, {username}!'
    }), 200


@api.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """Obtener información del usuario actual"""
    user_id = session.get('user_id')
    username = session.get('username')
    
    # Obtener progreso del usuario
    progress = firebase_service.get_user_progress(user_id)
    
    return jsonify({
        'success': True,
        'user': {
            'id': user_id,
            'username': username,
            'progress': progress
        }
    }), 200


# ============================================
# ENDPOINTS DE LECCIONES
# ============================================

@api.route('/lessons', methods=['GET'])
@login_required
def get_lessons():
    """
    Obtener todas las lecciones o filtradas por categoría
    
    Query params:
        ?category=Python Básico
    """
    category = request.args.get('category')
    
    if category:
        lessons = firebase_service.get_lessons_by_category(category)
    else:
        lessons = firebase_service.get_all_lessons()
    
    return jsonify({
        'success': True,
        'lessons': lessons,
        'count': len(lessons)
    }), 200


@api.route('/lessons/<lesson_id>', methods=['GET'])
@login_required
def get_lesson(lesson_id):
    """Obtener una lección específica"""
    lesson = firebase_service.get_lesson_by_id(lesson_id)
    
    if lesson:
        return jsonify({
            'success': True,
            'lesson': lesson
        }), 200
    else:
        return jsonify({
            'success': False,
            'message': 'Lección no encontrada'
        }), 404


@api.route('/lessons/categories', methods=['GET'])
@login_required
def get_categories():
    """Obtener lista de categorías disponibles"""
    from config import Config
    
    return jsonify({
        'success': True,
        'categories': Config.LESSON_CATEGORIES
    }), 200


@api.route("/search", methods=["GET"])
@login_required
def search():
    """
    Buscar lecciones
    Query param:
        ?q=variables
        ?q=variables&category=Python%20Basico
        ?q=variables&category=Python%20Intermedio&difficulty=2
    """
    query = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    difficulty = request.args.get("difficulty", type=int)

    if not query:
        return jsonify({
            "success": False,
            "message": "Parámetro de búsqueda vacío"
        }), 400

    # Usar busqueda avanzada si hay filtros
    if category or difficulty is not None:
        results = firebase_service.search_lessons_advanced(query, category, difficulty)
    else:
        results = firebase_service.search_lessons(query)

    return jsonify({
        "success": True,
        "query": query,
        "filters": {
            "category": category or None,
            "difficulty": difficulty
        },
        "results": results,
        "count": len(results)
    }), 200


# ============================================
# ENDPOINTS DE PROGRESO
# ============================================

@api.route('/progress', methods=['GET'])
@login_required
def get_progress():
    """Obtener progreso del usuario actual"""
    user_id = session.get('user_id')
    progress = firebase_service.get_user_progress(user_id)
    
    return jsonify({
        'success': True,
        'progress': progress
    }), 200


@api.route('/progress/complete/<lesson_id>', methods=['POST'])
@login_required
def complete_lesson(lesson_id):
    """Marcar una lección como completada"""
    user_id = session.get('user_id')
    
    success, message = firebase_service.update_user_progress(user_id, lesson_id, completed=True)
    
    if success:
        # Obtener progreso actualizado
        progress = firebase_service.get_user_progress(user_id)
        
        return jsonify({
            'success': True,
            'message': '¡Lección completada! +10 puntos',
            'progress': progress
        }), 200
    else:
        return jsonify({
            'success': False,
            'message': message
        }), 400


# ============================================
# ENDPOINT DE SALUD
# ============================================

@api.route('/health', methods=['GET'])
def health_check():
    """Verificar que la API está funcionando"""
    return jsonify({
        'success': True,
        'message': 'API funcionando correctamente',
        'version': '1.0.0'
    }), 200