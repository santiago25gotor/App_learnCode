from flask import Blueprint, request, jsonify, session
from backend.core.firebase import firebase_service
from backend.utils.decorators import login_required

user_api = Blueprint('user', __name__, url_prefix='/api/user')

@user_api.route('/me', methods=['GET'])
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


@user_api.route('/placement-test/submit', methods=['POST'])
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