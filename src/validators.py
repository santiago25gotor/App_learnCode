import re

def validate_email(email):
   
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password(password):
   
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"
    
    if not re.search(r'[A-Z]', password):
        return False, "Debe contener al menos una mayúscula"
    
    if not re.search(r'[a-z]', password):
        return False, "Debe contener al menos una minúscula"
    
    if not re.search(r'\d', password):
        return False, "Debe contener al menos un número"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Debe contener al menos un carácter especial"
    
    return True, "Contraseña válida"


def validate_username(username):
    
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]{2,19}$', username):
        return False, "El usuario debe tener 3-20 caracteres, comenzar con letra y solo contener letras, números y guiones bajos"
    
    return True, "Usuario válido"