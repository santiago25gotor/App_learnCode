from flask import Blueprint, request, jsonify, session
from backend.core.firebase import firebase_service
from backend.core.verification_service import generate_code, validate_code, send_verification_email
from backend.utils.validators import validate_email, validate_password, validate_username
from backend.utils.decorators import login_required
from firebase_admin import auth as firebase_auth
import requests as http
import time
from config import Config

auth_api = Blueprint('auth', __name__, url_prefix='/api/auth')

_send_log: dict = {}
MAX_SENDS_PER_HOUR = 5


def _rate_limited(email: str) -> bool:
    now = time.time()
    hist = [t for t in _send_log.get(email, []) if now - t < 3600]
    _send_log[email] = hist
    if len(hist) >= MAX_SENDS_PER_HOUR:
        return True
    hist.append(now)
    return False

@auth_api.route('/send-code', methods=['POST'])
def send_code():
    """Paso 1: Validar datos y enviar código de verificación al email"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'message': 'No se recibieron datos'}), 400

    username = data.get('username', '').strip().lower()
    email    = data.get('email',    '').strip().lower()
    password = data.get('password', '')

    is_valid, msg = validate_username(username)
    if not is_valid:
        return jsonify({'success': False, 'message': msg}), 400

    if not validate_email(email):
        return jsonify({'success': False, 'message': 'Formato de email inválido'}), 400

    is_valid, msg = validate_password(password)
    if not is_valid:
        return jsonify({'success': False, 'message': msg}), 400

    if firebase_service.user_exists(username=username):
        return jsonify({'success': False, 'message': 'El nombre de usuario ya existe'}), 400

    if firebase_service.user_exists(email=email):
        return jsonify({'success': False, 'message': 'El email ya está registrado'}), 400

    if _rate_limited(email):
        return jsonify({'success': False, 'message': 'Demasiadas solicitudes. Espera un momento.'}), 429

    code = generate_code(email)
    ok, message = send_verification_email(email, code, username)

    if not ok:
        return jsonify({'success': False, 'message': message}), 500

    return jsonify({'success': True, 'message': message}), 200


@auth_api.route('/register', methods=['POST'])
def register():
    """Paso 2: Verificar código y crear cuenta"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No se recibieron datos'}), 400

        username = data.get('username', '').strip().lower()
        email    = data.get('email',    '').strip().lower()
        password = data.get('password', '')
        code     = data.get('code',     '').strip()

        if not code:
            return jsonify({'success': False, 'message': 'Código de verificación requerido'}), 400

        ok, msg = validate_code(email, code)
        if not ok:
            return jsonify({'success': False, 'message': msg}), 400

        success, message, user_id = firebase_service.create_user(email, password, username)
        if not success:
            return jsonify({'success': False, 'message': message}), 400

        session['user_id']  = user_id
        session['username'] = username

        return jsonify({
            'success': True,
            'message': 'Cuenta creada correctamente. ¡Bienvenido!',
            'user':    {'id': user_id, 'username': username, 'email': email}
        }), 201

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error en el servidor: {str(e)}'}), 500


@auth_api.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No se recibieron datos'}), 400

        identifier = data.get('identifier', '').strip().lower()
        password   = data.get('password',   '')

        if '@' in identifier:
            email = identifier
        else:
            user = firebase_service.get_user_by_username(identifier)
            if not user:
                return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
            email = user['email']

        success, message, user_data = firebase_service.verify_user(email, password)
        if not success:
            return jsonify({'success': False, 'message': message}), 401

        session['user_id']  = user_data['uid']
        session['username'] = user_data['username']

        return jsonify({
            'success': True,
            'message': 'Login exitoso',
            'user': {
                'id':       user_data['uid'],
                'username': user_data['username'],
                'email':    user_data['email']
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error en el servidor: {str(e)}'}), 500


@auth_api.route('/logout', methods=['POST'])
@login_required
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Sesión cerrada'}), 200


@auth_api.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Cambiar contraseña desde el perfil (requiere sesión activa)"""
    try:
        data = request.get_json()
        user_id = session.get('user_id')

        new_password     = data.get('new_password',     '').strip()
        confirm_password = data.get('confirm_password', '').strip()

        if not new_password or not confirm_password:
            return jsonify({'success': False, 'message': 'Todos los campos son obligatorios'}), 400

        if new_password != confirm_password:
            return jsonify({'success': False, 'message': 'Las contraseñas no coinciden'}), 400

        is_valid, message = validate_password(new_password)
        if not is_valid:
            return jsonify({'success': False, 'message': message}), 400

        try:
            firebase_auth.update_user(user_id, password=new_password)
            return jsonify({'success': True, 'message': 'Contraseña actualizada exitosamente'}), 200
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error al actualizar contraseña: {str(e)}'}), 500

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error en el servidor: {str(e)}'}), 500


@auth_api.route('/forgot-password/send-code', methods=['POST'])
def forgot_password_send_code():
    """Enviar código de verificación para recuperar contraseña"""
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'success': False, 'message': 'No se recibieron datos'}), 400

        email = data.get('email', '').strip().lower()

        if not validate_email(email):
            return jsonify({'success': False, 'message': 'Formato de email inválido'}), 400

        user = firebase_service.get_user_by_email(email)
        if not user:
            
            return jsonify({'success': True, 'message': 'Si ese email existe en nuestra base de datos, recibirás un código de verificación.'}), 200

        if _rate_limited(email):
            return jsonify({'success': False, 'message': 'Demasiadas solicitudes. Espera un momento.'}), 429

        username = user.get('username', 'usuario')
        code = generate_code(email)
        ok, message = send_verification_email(email, code, username)

        if not ok:
            return jsonify({'success': False, 'message': message}), 500

        return jsonify({'success': True, 'message': 'Código enviado. Revisa tu bandeja de entrada.'}), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error en el servidor: {str(e)}'}), 500


@auth_api.route('/forgot-password/reset', methods=['POST'])
def forgot_password_reset():
    """Verificar código y establecer nueva contraseña"""
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'success': False, 'message': 'No se recibieron datos'}), 400

        email        = data.get('email',            '').strip().lower()
        code         = data.get('code',             '').strip()
        new_password = data.get('new_password',     '').strip()
        confirm_pass = data.get('confirm_password', '').strip()

        if not all([email, code, new_password, confirm_pass]):
            return jsonify({'success': False, 'message': 'Todos los campos son obligatorios'}), 400

        if new_password != confirm_pass:
            return jsonify({'success': False, 'message': 'Las contraseñas no coinciden'}), 400

        is_valid, msg = validate_password(new_password)
        if not is_valid:
            return jsonify({'success': False, 'message': msg}), 400

        ok, msg = validate_code(email, code)
        if not ok:
            return jsonify({'success': False, 'message': msg}), 400

        try:
            fb_user = firebase_auth.get_user_by_email(email)
            firebase_auth.update_user(fb_user.uid, password=new_password)
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error al actualizar la contraseña: {str(e)}'}), 500

        return jsonify({'success': True, 'message': '¡Contraseña actualizada! Ya puedes iniciar sesión.'}), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error en el servidor: {str(e)}'}), 500

@auth_api.route('/google', methods=['POST'])
def google_login():
    """Autenticación con Google mediante ID token de Firebase"""
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'success': False, 'message': 'No se recibieron datos'}), 400

        id_token = data.get('id_token', '').strip()
        if not id_token:
            return jsonify({'success': False, 'message': 'Token de Google requerido'}), 400

        try:
            decoded = firebase_auth.verify_id_token(id_token)
        except Exception as e:
            return jsonify({'success': False, 'message': f'Token inválido: {str(e)}'}), 401

        uid   = decoded['uid']
        email = decoded.get('email', '')
        name  = decoded.get('name', '')
        photo = decoded.get('picture', '')

        from firebase_admin import firestore

        user_ref = firebase_service.db.collection(Config.USERS_COLLECTION).document(uid)
        user_doc = user_ref.get()

        if user_doc.exists:
            user_data = user_doc.to_dict()
            username  = user_data.get('username', email.split('@')[0])
        else:
            base_username = (name.replace(' ', '_').lower() or email.split('@')[0])[:20]
            import re
            base_username = re.sub(r'[^a-z0-9_]', '', base_username)
            if not base_username or not base_username[0].isalpha():
                base_username = 'user_' + base_username

            username = base_username
            counter  = 1
            while firebase_service.user_exists(username=username):
                username = f"{base_username}{counter}"
                counter += 1

            user_ref.set({
                'username':      username,
                'email':         email,
                'photo_url':     photo,
                'role':          'user',
                'auth_provider': 'google',
                'created_at':    firestore.SERVER_TIMESTAMP,
                'progress': {
                    'completed_lessons':       [],
                    'current_level':           'Python Básico',
                    'total_points':            0,
                    'unlocked_categories':     ['Python Básico'],
                    'placement_test_completed': False
                }
            })

        session['user_id']  = uid
        session['username'] = username

        return jsonify({
            'success': True,
            'message': 'Login con Google exitoso',
            'is_new':  not user_doc.exists,
            'user': {
                'id':       uid,
                'username': username,
                'email':    email,
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error en el servidor: {str(e)}'}), 500