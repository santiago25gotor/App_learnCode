from flask import Blueprint, request, jsonify, session
from backend.core.firebase import firebase_service
from backend.utils.decorators import login_required

user_api = Blueprint('user', __name__, url_prefix='/api/user')

@user_api.route('/me', methods=['GET'])
@login_required
def get_current_user():
    user_id = session.get('user_id')
    username = session.get('username')

    user_doc = firebase_service.db.collection('users').document(user_id).get()
    user_data = user_doc.to_dict() if user_doc.exists else {}

    progress = user_data.get('progress', {})
    avatar = user_data.get('avatar', '')

    return jsonify({
        'success': True,
        'user': {
            'id': user_id,
            'username': user_data.get('username', username),
            'email': user_data.get('email', ''),
            'avatar': avatar,
            'role': user_data.get('role', 'user'),
            'progress': progress
        }
    }), 200

@user_api.route('/avatar', methods=['PUT'])
@login_required
def update_avatar():
    try:
        user_id = session.get('user_id')
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'message': 'No se recibieron datos'
            }), 400

        avatar_url = data.get('avatar', '')

        firebase_service.db.collection('users') \
            .document(user_id) \
            .update({'avatar': avatar_url})

        return jsonify({
            'success': True,
            'avatar': avatar_url
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@user_api.route('/placement-test/submit', methods=['POST'])
@login_required
def submit_placement_test():
    try:
        user_id = session.get('user_id')
        data    = request.get_json()
        scores  = data.get('scores', {})

        unlocked_categories = ['Python Básico']  # Siempre desbloqueado
        lessons_unlocked    = 0
        nivel               = None

        # ── Formato 1: score total único (0-100) ──────────────────────────────
        # Enviado por placement_test.html → { scores: { total: 85 } }
        if 'total' in scores:
            total_score = scores.get('total', 0)

            if total_score <= 50:
                nivel = 'Básico'
            elif total_score <= 79:
                nivel = 'Intermedio'
            else:
                nivel = 'Avanzado'

            if nivel in ('Intermedio', 'Avanzado'):
                unlocked_categories.append('Python Intermedio')
                ok, count = firebase_service.unlock_all_lessons_for_category(user_id, 'Python Básico')
                print(f"[PLACEMENT] unlock_all_lessons 'Python Básico' -> ok={ok}, count={count}")
                if ok:
                    lessons_unlocked += count

            if nivel == 'Avanzado':
                unlocked_categories.append('Python Avanzado')
                ok, count = firebase_service.unlock_all_lessons_for_category(user_id, 'Python Intermedio')
                print(f"[PLACEMENT] unlock_all_lessons 'Python Intermedio' -> ok={ok}, count={count}")
                if ok:
                    lessons_unlocked += count

        # ── Formato 2: scores por categoría separados ─────────────────────────
        # Enviado por otros frontends → { scores: { basic: 80, intermediate: 75, advanced: 60 } }
        else:
            basic_score        = scores.get('basic', 0)
            intermediate_score = scores.get('intermediate', 0)
            advanced_score     = scores.get('advanced', 0)

            if basic_score >= 70:
                unlocked_categories.append('Python Intermedio')
                ok, count = firebase_service.unlock_all_lessons_for_category(user_id, 'Python Básico')
                if ok:
                    lessons_unlocked += count

            if intermediate_score >= 75:
                unlocked_categories.append('Python Avanzado')
                ok, count = firebase_service.unlock_all_lessons_for_category(user_id, 'Python Intermedio')
                if ok:
                    lessons_unlocked += count

            if advanced_score >= 80:
                ok, count = firebase_service.unlock_all_lessons_for_category(user_id, 'Python Avanzado')
                if ok:
                    lessons_unlocked += count

        firebase_service.save_placement_test_results(user_id, scores, unlocked_categories)

        print(f"[PLACEMENT] nivel={nivel}, unlocked_categories={unlocked_categories}, lessons_unlocked={lessons_unlocked}")

        msg = f'Test completado. {lessons_unlocked} lecciones desbloqueadas.'
        if nivel:
            msg = f'Test completado. Nivel: {nivel}. {lessons_unlocked} lecciones desbloqueadas.'

        return jsonify({
            'success':             True,
            'scores':              scores,
            'nivel':               nivel,
            'unlocked_categories': unlocked_categories,
            'lessons_unlocked':    lessons_unlocked,
            'message':             msg
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500