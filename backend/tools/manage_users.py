import sys
import os
import argparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.firebase import firebase_service
from config import Config

def main():
    parser = argparse.ArgumentParser(description="Gestión de usuarios PYLEARN")
    parser.add_argument("--action", choices=["create", "unlock", "delete"], required=True)
    parser.add_argument("--role", choices=["user", "admin"], default="user")
    parser.add_argument("--email", required=True)
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", default="Test1234!")

    args = parser.parse_args()

    print(f"--- Iniciando acción: {args.action.upper()} ---")

    if args.action == "create":
        success, msg, uid = firebase_service.create_user(args.email, args.password, args.username)
        if not success:
            print(f"Error: {msg}")
            return
        
        if args.role == "admin":
            firebase_service.db.collection(Config.USERS_COLLECTION).document(uid).update({'role': 'admin'})
        
        print(f"Desbloqueando lecciones para {args.username}...")
        ok, count = firebase_service.mass_unlock_lessons(uid)
        if ok:
            print(f"Éxito: Usuario {uid} creado con {count} lecciones desbloqueadas.")

    elif args.action == "unlock":
        
        user = firebase_service.get_user_by_email(args.email)
        if user:
            ok, count = firebase_service.mass_unlock_lessons(user['uid'])
            print(f"Se han desbloqueado {count} lecciones adicionales.")
        else:
            print("Usuario no encontrado.")

if __name__ == "__main__":
    main()