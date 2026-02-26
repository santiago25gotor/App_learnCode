from flask import Blueprint, request, jsonify, session
from backend.core.firebase import firebase_service
from backend.utils.decorators import login_required
from config import Config

admin_api = Blueprint('admin', __name__, url_prefix='/api/admin')


def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'No autenticado'}), 401
        user_id = session.get('user_id')
        try:
            user_doc = firebase_service.db.collection(Config.USERS_COLLECTION).document(user_id).get()
            if not user_doc.exists or user_doc.to_dict().get('role') != 'admin':
                return jsonify({'success': False, 'message': 'Acceso denegado'}), 403
        except Exception:
            return jsonify({'success': False, 'message': 'Error verificando permisos'}), 500
        return f(*args, **kwargs)
    return decorated


@admin_api.route('/stats', methods=['GET'])
@admin_required
def get_stats():
    try:
        users = firebase_service.db.collection(Config.USERS_COLLECTION).get()
        lessons = firebase_service.db.collection(Config.LESSONS_COLLECTION).get()

        users_list = [u.to_dict() for u in users]
        total_users = len(users_list)
        total_lessons = len(list(lessons))

        total_points = sum(
            u.get('progress', {}).get('total_points', 0)
            for u in users_list
        )
        avg_points = round(total_points / total_users, 1) if total_users > 0 else 0

        active_users = sum(
            1 for u in users_list
            if len(u.get('progress', {}).get('completed_lessons', [])) > 0
        )

        return jsonify({
            'success': True,
            'stats': {
                'total_users': total_users,
                'total_lessons': total_lessons,
                'avg_points': avg_points,
                'active_users': active_users,
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_api.route('/users', methods=['GET'])
@admin_required
def get_users():
    try:
        search = request.args.get('search', '').lower()
        docs = firebase_service.db.collection(Config.USERS_COLLECTION).get()

        users = []
        for doc in docs:
            data = doc.to_dict()
            progress = data.get('progress', {})
            user = {
                'id': doc.id,
                'username': data.get('username', ''),
                'email': data.get('email', ''),
                'role': data.get('role', 'user'),
                'total_points': progress.get('total_points', 0),
                'completed_lessons': len(progress.get('completed_lessons', [])),
                'level': progress.get('current_level', 'Python Básico'),
                'placement_done': progress.get('placement_test_completed', False),
            }
            if search:
                if search not in user['username'].lower() and search not in user['email'].lower():
                    continue
            users.append(user)

        users.sort(key=lambda x: x['total_points'], reverse=True)
        return jsonify({'success': True, 'users': users, 'count': len(users)}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_api.route('/users/<user_id>', methods=['GET'])
@admin_required
def get_user_detail(user_id):
    try:
        doc = firebase_service.db.collection(Config.USERS_COLLECTION).document(user_id).get()
        if not doc.exists:
            return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
        data = doc.to_dict()
        data['id'] = doc.id
        return jsonify({'success': True, 'user': data}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_api.route('/users/<user_id>/role', methods=['PUT'])
@admin_required
def update_user_role(user_id):
    try:
        data = request.get_json()
        new_role = data.get('role')
        if new_role not in ['user', 'admin']:
            return jsonify({'success': False, 'message': 'Rol inválido'}), 400

        if user_id == session.get('user_id') and new_role != 'admin':
            return jsonify({'success': False, 'message': 'No puedes quitarte el rol admin'}), 400

        firebase_service.db.collection(Config.USERS_COLLECTION).document(user_id).update({'role': new_role})
        return jsonify({'success': True, 'message': f'Rol actualizado a {new_role}'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_api.route('/users/<user_id>/unlock', methods=['POST'])
@admin_required
def unlock_user_lessons(user_id):
    try:
        ok, result = firebase_service.mass_unlock_lessons(user_id)
        if ok:
            return jsonify({'success': True, 'message': f'{result} lecciones desbloqueadas'}), 200
        return jsonify({'success': False, 'message': str(result)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_api.route('/users/<user_id>/reset', methods=['POST'])
@admin_required
def reset_user_progress(user_id):
    """Resetear el progreso de un usuario"""
    try:
        if user_id == session.get('user_id'):
            return jsonify({'success': False, 'message': 'No puedes resetear tu propio progreso'}), 400

        empty_progress = {
            'completed_lessons': [],
            'total_points': 0,
            'current_level': 'Python Básico',
            'unlocked_categories': ['Python Básico'],
            'placement_test_completed': False,
        }
        firebase_service.db.collection(Config.USERS_COLLECTION).document(user_id).update(
            {'progress': empty_progress}
        )
        return jsonify({'success': True, 'message': 'Progreso reseteado'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_api.route('/users/<user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Eliminar un usuario"""
    try:
        if user_id == session.get('user_id'):
            return jsonify({'success': False, 'message': 'No puedes eliminarte a ti mismo'}), 400

        from firebase_admin import auth
        firebase_service.db.collection(Config.USERS_COLLECTION).document(user_id).delete()
        try:
            auth.delete_user(user_id)
        except Exception:
            pass  # Si no existe en Auth, igual borramos Firestore

        return jsonify({'success': True, 'message': 'Usuario eliminado'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_api.route('/check', methods=['GET'])
@login_required
def check_admin():
    """Verificar si el usuario actual es admin"""
    try:
        user_id = session.get('user_id')
        doc = firebase_service.db.collection(Config.USERS_COLLECTION).document(user_id).get()
        is_admin = doc.exists and doc.to_dict().get('role') == 'admin'
        return jsonify({'success': True, 'is_admin': is_admin}), 200
    except Exception:
        return jsonify({'success': True, 'is_admin': False}), 200
