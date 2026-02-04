"""
Sistema de autenticación adaptado para Firebase
Basado en tu código original de auth.py
"""
import getpass
from backend.validators import validate_email, validate_password, validate_username
from backend.firebase_service import firebase_service


class AuthSystem:
    """Sistema de autenticación que usa Firebase"""
    
    def __init__(self):
        self.firebase = firebase_service
        self.current_user = None
        self.current_user_id = None
    
    def register(self):
        """Registro de usuario - Compatible con tu código original"""
        print("\n=== REGISTRO DE USUARIO ===\n")
        
        # Validar y obtener username
        while True:
            username = input("Usuario: ").strip().lower()
            is_valid, message = validate_username(username)
            if is_valid:
                if self.firebase.user_exists(username=username):
                    print("❌ El usuario ya existe. Intenta con otro.\n")
                else:
                    break
            else:
                print(f"❌ {message}\n")
        
        # Validar y obtener email
        while True:
            email = input("Email: ").strip().lower()
            if validate_email(email):
                if self.firebase.user_exists(email=email):
                    print("❌ El email ya está registrado.\n")
                else:
                    break
            else:
                print("❌ Formato de email inválido\n")
        
        # Validar y obtener contraseña
        while True:
            password = getpass.getpass("Contraseña: ")
            is_valid, message = validate_password(password)
            if is_valid:
                password_confirm = getpass.getpass("Confirmar contraseña: ")
                if password == password_confirm:
                    break
                else:
                    print("❌ Las contraseñas no coinciden\n")
            else:
                print(f"❌ {message}\n")
        
        # Crear usuario en Firebase
        success, message, user_id = self.firebase.create_user(email, password, username)
        
        if success:
            print(f"\n✅ {message}")
            print(f"Usuario creado: {username}")
            print(f"ID de Firebase: {user_id}")
            return True
        else:
            print(f"\n❌ {message}")
            return False
    
    def login(self):
        """
        Inicio de sesión
        
        Nota: En producción, la verificación de contraseña se hace en el cliente
        con Firebase Auth SDK. Esta es una versión simplificada para desarrollo.
        """
        print("\n=== INICIO DE SESIÓN ===\n")
        
        # Permitir login con username o email
        identifier = input("Usuario o Email: ").strip().lower()
        password = getpass.getpass("Contraseña: ")
        
        # Determinar si es email o username
        if '@' in identifier:
            # Es un email
            success, message, user_data = self.firebase.verify_user(identifier, password)
        else:
            # Es un username, buscar el email asociado
            user = self.firebase.get_user_by_username(identifier)
            if user:
                success, message, user_data = self.firebase.verify_user(user['email'], password)
            else:
                print("\n❌ Usuario no encontrado")
                return False
        
        if success:
            self.current_user = user_data['username']
            self.current_user_id = user_data['uid']
            print(f"\n✅ {message}")
            print(f"¡Bienvenido, {self.current_user}! 🎉")
            return True
        else:
            print(f"\n❌ {message}")
            return False
    
    def logout(self):
        """Cerrar sesión"""
        if self.current_user:
            print(f"\n👋 Hasta luego, {self.current_user}!")
            self.current_user = None
            self.current_user_id = None
        else:
            print("\n⚠️  No hay sesión activa")
    
    def is_logged_in(self):
        """Verificar si hay sesión activa"""
        return self.current_user is not None
    
    def get_current_user_id(self):
        """Obtener el ID del usuario actual"""
        return self.current_user_id
    
    def get_current_username(self):
        """Obtener el nombre del usuario actual"""
        return self.current_user


# Para compatibilidad con tu código original
if __name__ == "__main__":
    # Ejemplo de uso
    auth = AuthSystem()
    
    while True:
        print("\n" + "="*50)
        print("1. Registrarse")
        print("2. Iniciar sesión")
        print("3. Cerrar sesión")
        print("4. Salir")
        print("="*50)
        
        opcion = input("\nSelecciona una opción: ").strip()
        
        if opcion == "1":
            auth.register()
        elif opcion == "2":
            auth.login()
        elif opcion == "3":
            auth.logout()
        elif opcion == "4":
            print("\n👋 ¡Hasta pronto!")
            break
        else:
            print("\n❌ Opción inválida")