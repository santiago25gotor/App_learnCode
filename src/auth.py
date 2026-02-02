
import getpass
from .validators import validate_email, validate_password, validate_username
from .database import Database

class AuthSystem:
    def __init__(self):
        self.db = Database()
        self.current_user = None
    
    def register(self):
        print("\n=== REGISTRO DE USUARIO ===\n")
        
        while True:
            username = input("Usuario: ").strip().lower()
            is_valid, message = validate_username(username)
            if is_valid:
                if self.db.user_exists(username):
                    print(" El usuario ya existe. Intenta con otro.\n")
                else:
                    break
            else:
                print(f" {message}\n")
        
      
        while True:
            email = input("Email: ").strip().lower()
            if validate_email(email):
                if self.db.email_exists(email):
                    print(" El email ya está registrado.\n")
                else:
                    break
            else:
                print(" Formato de email inválido\n")
        

        while True:
            password = getpass.getpass("Contraseña: ")
            is_valid, message = validate_password(password)
            if is_valid:
                password_confirm = getpass.getpass("Confirmar contraseña: ")
                if password == password_confirm:
                    break
                else:
                    print(" Las contraseñas no coinciden\n")
            else:
                print(f" {message}\n")
        
        success, message = self.db.register_user(username, email, password)
        if success:
            print(f"\n {message}")
            return True
        else:
            print(f"\n {message}")
            return False
    
    def login(self):
        
        print("\n=== INICIO DE SESIÓN ===\n")
        
        username = input("Usuario: ").strip().lower()
        password = getpass.getpass("Contraseña: ")
        
        success, message = self.db.authenticate(username, password)
        
        if success:
            self.current_user = username
            print(f"\n {message}")
            print(f"Bienvenido, {username}! 🎉")
            return True
        else:
            print(f"\n {message}")
            return False
    
    def logout(self):
        
        if self.current_user:
            print(f"\n Hasta luego, {self.current_user}!")
            self.current_user = None
        else:
            print("\n  No hay sesión activa")
    
    def is_logged_in(self):
        return self.current_user is not None