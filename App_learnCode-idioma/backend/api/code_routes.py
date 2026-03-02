from flask import Blueprint, request, jsonify, session
import io
import traceback
import functools
import time
import math
import random
import datetime
import collections
import itertools
import string
import re
from contextlib import redirect_stdout, redirect_stderr
from backend.utils.decorators import login_required
from data.exams_data import EXAMS 

code_api = Blueprint('code', __name__, url_prefix='/api/code')

# Módulos permitidos en el compilador online
ALLOWED_MODULES = {
    'functools', 'time', 'math', 'random', 'datetime',
    'collections', 'itertools', 'string', 're'
}

# Mapa de módulos ya importados para inyectarlos directamente
PRELOADED_MODULES = {
    'functools': functools,
    'time': time,
    'math': math,
    'random': random,
    'datetime': datetime,
    'collections': collections,
    'itertools': itertools,
    'string': string,
    're': re,
}

def make_safe_import(preloaded):
    def safe_import(name, *args, **kwargs):
        if name in ALLOWED_MODULES:
            return preloaded[name]
        raise ImportError(f"Módulo '{name}' no está permitido en el compilador online")
    return safe_import

@code_api.route('/execute', methods=['POST'])
@login_required
def execute_code():
    try:
        data = request.get_json()
        code = data.get('code', '')
        
        if not code:
            return jsonify({'success': False, 'message': 'No hay código'}), 400

        stdout_capture, stderr_capture = io.StringIO(), io.StringIO()

        safe_globals = {
            '__builtins__': {
                # Built-ins básicos
                'print': print, 'len': len, 'range': range, 'str': str, 
                'int': int, 'float': float, 'bool': bool, 'list': list, 
                'dict': dict, 'tuple': tuple, 'set': set, 'abs': abs, 
                'max': max, 'min': min, 'sum': sum, 'sorted': sorted,
                'enumerate': enumerate, 'zip': zip, 'type': type,
                'True': True, 'False': False, 'None': None,
                'isinstance': isinstance, 'hasattr': hasattr,
                'getattr': getattr, 'setattr': setattr,
                'map': map, 'filter': filter, 'any': any, 'all': all,
                'round': round, 'pow': pow, 'divmod': divmod,
                'hex': hex, 'oct': oct, 'bin': bin, 'ord': ord, 'chr': chr,
                'repr': repr, 'hash': hash, 'id': id,
                'reversed': reversed, 'next': next, 'iter': iter,
                'open': None,  # Bloqueado explícitamente
                # Import seguro
                '__import__': make_safe_import(PRELOADED_MODULES),
            }
        }
        
        try:
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                exec(code, safe_globals)
            
            return jsonify({
                'success': True,
                'output': stdout_capture.getvalue() or '(Sin salida)',
                'error': stderr_capture.getvalue() or None
            }), 200
        except Exception:
            return jsonify({'success': False, 'error': traceback.format_exc()}), 200
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@code_api.route('/exams/<category>', methods=['GET'])
@login_required
def get_exam(category):
    exam = EXAMS.get(category)
    if not exam:
        return jsonify({'success': False, 'message': 'Examen no encontrado'}), 404
    
    return jsonify({'success': True, 'exam': exam}), 200

@code_api.route('/exams/<exam_id>/submit', methods=['POST'])
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