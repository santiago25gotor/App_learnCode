from flask import Blueprint, request, jsonify, session
from backend.core.firebase import firebase_service 
from backend.utils.validators import validate_email, validate_password, validate_username
from backend.utils.decorators import login_required
from firebase_admin import auth as firebase_auth

# Crear Blueprint para las rutas de la API
auth_api = Blueprint('auth', __name__, url_prefix='/api/auth')



@auth_api.route('/register', methods=['POST'])
def register():
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


@auth_api.route('/login', methods=['POST'])
def login():
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


@auth_api.route('/logout', methods=['POST'])
@login_required
def logout():
    """Cerrar sesión"""
    session.clear()
    return jsonify({
        'success': True,
        'message': 'Sesión cerrada'
    }), 200


@auth_api.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Cambiar contraseña del usuario"""
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        
        new_password = data.get('new_password', '').strip()
        confirm_password = data.get('confirm_password', '').strip()
        
        # Validaciones básicas
        if not new_password or not confirm_password:
            return jsonify({
                'success': False,
                'message': 'Todos los campos son obligatorios'
            }), 400
        
        if new_password != confirm_password:
            return jsonify({
                'success': False,
                'message': 'Las contraseñas no coinciden'
            }), 400
        
        # Validar contraseña con validate_password
        is_valid, message = validate_password(new_password)
        if not is_valid:
            return jsonify({
                'success': False,
                'message': message
            }), 400
        
        # Cambiar contraseña en Firebase Auth
        try:
            firebase_auth.update_user(
                user_id,
                password=new_password
            )
            
            return jsonify({
                'success': True,
                'message': 'Contraseña actualizada exitosamente'
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error al actualizar contraseña: {str(e)}'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error en el servidor: {str(e)}'
        }), 500