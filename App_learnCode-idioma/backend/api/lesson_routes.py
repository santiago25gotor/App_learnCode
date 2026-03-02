from flask import Blueprint, request, jsonify, session
from backend.core.firebase import firebase_service
from backend.utils.decorators import login_required

lesson_api = Blueprint('lesson', __name__)

@lesson_api.route('/', methods=['GET'])
@login_required
def get_lessons():
    category = request.args.get('category')
    lessons = firebase_service.get_lessons_by_category(category) if category else firebase_service.get_all_lessons()
    return jsonify({'success': True, 'lessons': lessons, 'count': len(lessons)}), 200

'''
@lesson_api.route('/<lesson_id>', methods=['GET'])
@login_required
def get_lesson(lesson_id):
    user_id = session.get('user_id')
    lesson = firebase_service.get_lesson_by_id(lesson_id)
    
    if lesson:
        # Comprobar si esta ID está en la lista de completadas del usuario
        user_progress = firebase_service.get_user_progress(user_id)
        # Asumiendo que user_progress tiene una lista o dict de lecciones completadas
        is_completed = lesson_id in user_progress.get('completed_lessons', [])

        return jsonify({
            'success': True,
            'lesson': lesson,
            'is_completed': is_completed 
        }), 200
    
    else:
        return jsonify({
            'success': False,
            'message': 'Lección no encontrada'
        }), 404
'''
    
@lesson_api.route('/<lesson_id>', methods=['GET'])
@login_required
def get_lesson(lesson_id):
    user_id = session.get('user_id')
    lesson = firebase_service.get_lesson_by_id(lesson_id)
    
    if lesson:
        user_progress = firebase_service.get_user_progress(user_id)
        completed_lessons = user_progress.get('completed_lessons', [])
        
        is_completed = lesson_id in completed_lessons
        
        all_lessons = firebase_service.get_all_lessons()
        all_lessons.sort(key=lambda x: x.get('numero_leccion', 0))
        
        is_locked = False
        lesson_index = next((i for i, l in enumerate(all_lessons) if l.get('id') == lesson_id), None)
        
        if lesson_index is not None and lesson_index > 0:
            previous_lesson = all_lessons[lesson_index - 1]
            if previous_lesson.get('id') not in completed_lessons:
                is_locked = True

        return jsonify({
            'success': True,
            'lesson': lesson,
            'is_completed': is_completed,
            'is_locked': is_locked,  
            'is_preview': is_locked  
        }), 200
    
    else:
        return jsonify({
            'success': False,
            'message': 'Lección no encontrada'
        }), 404

@lesson_api.route('/categories', methods=['GET'])
@login_required
def get_categories():
    from config import Config
    
    return jsonify({
        'success': True,
        'categories': Config.LESSON_CATEGORIES
    }), 200


@lesson_api.route("/search", methods=["GET"])
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


@lesson_api.route('/complete/<lesson_id>', methods=['POST'])
@login_required
def complete_lesson(lesson_id):
    
    user_id = session.get('user_id')
    
    success, message = firebase_service.update_user_progress(user_id, lesson_id, completed=True)
    
    if success:
        
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



@lesson_api.route('/health', methods=['GET'])
def health_check():

    return jsonify({
        'success': True,
        'message': 'API funcionando correctamente',
        'version': '1.0.0'
    }), 200
