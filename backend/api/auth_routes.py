from flask import Blueprint, request, jsonify, session
from backend.core.firebase import firebase_service
from backend.core.verification_service import generate_code, validate_code, send_verification_email
from backend.utils.validators import validate_email, validate_password, validate_username
from backend.utils.decorators import login_required
import requests as http
import time
from config import Config

auth_api = Blueprint('auth', __name__, url_prefix='/api/auth')

_send_log: dict = {}   
MAX_SENDS_PER_HOUR = 5

def _rate_limited(email: str) -> bool:
    now  = time.time()
    hist = [t for t in _send_log.get(email, []) if now - t < 3600]
    _send_log[email] = hist
    if len(hist) >= MAX_SENDS_PER_HOUR:
        return True
    hist.append(now)
    return False


def _firebase_sign_in(email: str, password: str) -> dict | None:
    url = (
        "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
        f"?key={Config.FIREBASE_WEB_API_KEY}"
    )
    try:
        res = http.post(url, json={"email": email, "password": password, "returnSecureToken": True}, timeout=8)
        return res.json() if res.status_code == 200 else None
    except Exception:
        return None


@auth_api.route('/send-code', methods=['POST'])
def send_code():
    
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
