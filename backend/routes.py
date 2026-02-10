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
    session.clear()
    return jsonify({
        'success': True,
        'message': 'Sesión cerrada'
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


@api.route('/placement-test/submit', methods=['POST'])
@login_required
def submit_placement_test():
    """Guardar resultados del placement test y desbloquear niveles"""
    try:
        user_id = session.get('user_id')
        data = request.get_json()
        scores = data.get('scores', {})
        
        basic_score = scores.get('basic', 0)
        intermediate_score = scores.get('intermediate', 0)
        advanced_score = scores.get('advanced', 0)
        
        # Desbloquear niveles según puntuación
        unlocked_categories = ['Python Básico']  # Siempre desbloqueado
        lessons_unlocked = 0
        
        # Si aprueba básico, desbloquear todas las lecciones básicas y dar acceso a intermedio
        if basic_score >= 70:
            unlocked_categories.append('Python Intermedio')
            # Marcar todas las lecciones básicas como completadas
            success, count = firebase_service.unlock_all_lessons_for_category(user_id, 'Python Básico')
            if success:
                lessons_unlocked += count
        
        # Si aprueba intermedio, desbloquear todas las lecciones intermedias y dar acceso a avanzado
        if intermediate_score >= 75:
            unlocked_categories.append('Python Avanzado')
            # Marcar todas las lecciones intermedias como completadas
            success, count = firebase_service.unlock_all_lessons_for_category(user_id, 'Python Intermedio')
            if success:
                lessons_unlocked += count
        
        # Si aprueba avanzado, desbloquear todas las avanzadas
        if advanced_score >= 80:
            success, count = firebase_service.unlock_all_lessons_for_category(user_id, 'Python Avanzado')
            if success:
                lessons_unlocked += count
        
        # Guardar resultados en Firebase
        firebase_service.save_placement_test_results(user_id, scores, unlocked_categories)
        
        return jsonify({
            'success': True,
            'scores': scores,
            'unlocked_categories': unlocked_categories,
            'lessons_unlocked': lessons_unlocked,
            'message': f'Test completado. {lessons_unlocked} lecciones desbloqueadas.'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500



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


# ============================================
# ENDPOINTS PARA EJECUCIÓN DE CÓDIGO
# ============================================

@api.route('/execute', methods=['POST'])
@login_required
def execute_code():
    """Endpoint para ejecutar código Python de forma segura"""
    try:
        data = request.get_json()
        code = data.get('code', '')
        
        if not code:
            return jsonify({
                'success': False,
                'message': 'No se proporcionó código para ejecutar'
            }), 400
        
        import io
        import sys
        from contextlib import redirect_stdout, redirect_stderr
        import traceback
        
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        safe_globals = {
            '__builtins__': {
                'print': print,
                'len': len,
                'range': range,
                'str': str,
                'int': int,
                'float': float,
                'bool': bool,
                'list': list,
                'dict': dict,
                'tuple': tuple,
                'set': set,
                'abs': abs,
                'max': max,
                'min': min,
                'sum': sum,
                'sorted': sorted,
                'enumerate': enumerate,
                'zip': zip,
                'map': map,
                'filter': filter,
                'type': type,
                'isinstance': isinstance,
                'round': round,
                'pow': pow,
                'divmod': divmod,
                'hex': hex,
                'oct': oct,
                'bin': bin,
                'chr': chr,
                'ord': ord,
                'reversed': reversed,
                'any': any,
                'all': all,
                'input': lambda prompt='': '',  # input simulado
                'True': True,
                'False': False,
                'None': None,
            }
        }
        
        try:
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                exec(code, safe_globals)
            
            output = stdout_capture.getvalue()
            error = stderr_capture.getvalue()
            
            return jsonify({
                'success': True,
                'output': output if output else '(Sin salida)',
                'error': error if error else None
            }), 200
            
        except Exception as e:
            error_trace = traceback.format_exc()
            return jsonify({
                'success': False,
                'output': '',
                'error': error_trace
            }), 200
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error del servidor: {str(e)}'
        }), 500


# ============================================
# ENDPOINTS PARA EXÁMENES
# ============================================

@api.route('/exams/<category>', methods=['GET'])
@login_required
def get_exam(category):
    """Obtener examen para una categoría específica"""
    try:
        exams = {
            'Python Básico': {
                'id': 'exam_basico',
                'title': 'Examen: Python Básico',
                'description': 'Demuestra tu conocimiento en fundamentos de Python',
                'time_limit': 30,
                'passing_score': 70,
                'questions': [
                    {
                        'id': 'q1',
                        'type': 'multiple_choice',
                        'question': '¿Cuál es la salida de: print(type(5))?',
                        'options': [
                            "<class 'int'>",
                            "<class 'float'>",
                            "<class 'str'>",
                            '5'
                        ],
                        'correct': 0,
                        'points': 10
                    },
                    {
                        'id': 'q2',
                        'type': 'code',
                        'question': 'Escribe una función que sume dos números',
                        'starter_code': 'def sumar(a, b):\n    # Tu código aquí\n    pass',
                        'test_cases': [
                            {'input': [2, 3], 'expected': 5},
                            {'input': [10, 5], 'expected': 15},
                            {'input': [-1, 1], 'expected': 0}
                        ],
                        'points': 20
                    }
                ]
            },
            'Python Intermedio': {
                'id': 'exam_intermedio',
                'title': 'Examen: Python Intermedio',
                'description': 'Evalúa tus habilidades en estructuras de datos',
                'time_limit': 45,
                'passing_score': 75,
                'questions': [
                    {
                        'id': 'q1',
                        'type': 'code',
                        'question': 'Crea una función que filtre números pares',
                        'starter_code': 'def filtrar_pares(lista):\n    # Tu código aquí\n    pass',
                        'test_cases': [
                            {'input': [[1,2,3,4,5,6]], 'expected': [2,4,6]}
                        ],
                        'points': 25
                    }
                ]
            },
            'Python Avanzado': {
                'id': 'exam_avanzado',
                'title': 'Examen: Python Avanzado',
                'description': 'Demuestra dominio en programación avanzada',
                'time_limit': 60,
                'passing_score': 80,
                'questions': [
                    {
                        'id': 'q1',
                        'type': 'code',
                        'question': 'Implementa un decorador',
                        'starter_code': 'def decorador(func):\n    # Tu código aquí\n    pass',
                        'test_cases': [],
                        'points': 30
                    }
                ]
            }
        }
        
        exam = exams.get(category)
        
        if not exam:
            return jsonify({
                'success': False,
                'message': 'Examen no encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'exam': exam
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


@api.route('/exams/<exam_id>/submit', methods=['POST'])
@login_required
def submit_exam(exam_id):
    """Enviar respuestas del examen"""
    try:
        user_id = session.get('user_id')
        data = request.get_json()
        answers = data.get('answers', {})
        
        score = 85
        passed = score >= 70
        
        return jsonify({
            'success': True,
            'score': score,
            'passed': passed,
            'message': '¡Felicidades!' if passed else 'Intenta de nuevo'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500