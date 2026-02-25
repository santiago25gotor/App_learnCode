import sys
import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

import argparse
from backend.core.firebase import firebase_service
from config import Config


def main():
    parser = argparse.ArgumentParser(description="Gestión de usuarios PYLEARN")
    parser.add_argument("--action",   choices=["create", "unlock", "delete"], required=True)
    parser.add_argument("--role",     choices=["user", "admin"], default="user")
    parser.add_argument("--email",    required=True)
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", default="Test1234!")

    args = parser.parse_args()

    print(f"\n--- Iniciando acción: {args.action.upper()} ---")

    if args.action == "create":
        
        success, msg, uid = firebase_service.create_user(args.email, args.password, args.username)
        if not success:
            print(f"❌  Error al crear usuario: {msg}")
            return

        print(f"✅  Usuario creado — UID: {uid}")

        if args.role == "admin":
            firebase_service.db.collection(Config.USERS_COLLECTION).document(uid).update({"role": "admin"})
            print(f"✅  Rol asignado: admin")
 
        print(f"🔓  Desbloqueando lecciones para '{args.username}'...")
        ok, count = firebase_service.mass_unlock_lessons(uid)
        if ok:
            print(f"✅  {count} lecciones desbloqueadas.")
        else:
            print(f"⚠️   No se pudieron desbloquear las lecciones: {count}")

    elif args.action == "unlock":
        user = firebase_service.get_user_by_email(args.email)
        if not user:
            print("❌  Usuario no encontrado.")
            return
        ok, count = firebase_service.mass_unlock_lessons(user["uid"])
        if ok:
            print(f"✅  {count} lecciones desbloqueadas para '{args.email}'.")
        else:
            print(f"⚠️   Error al desbloquear: {count}")

    elif args.action == "delete":
        user = firebase_service.get_user_by_email(args.email)
        if not user:
            print("❌  Usuario no encontrado.")
            return

        uid = user["uid"]
        firebase_service.db.collection(Config.USERS_COLLECTION).document(uid).delete()

        try:
            from firebase_admin import auth
            auth.delete_user(uid)
        except Exception:
            pass  

        print(f"✅  Usuario '{args.email}' eliminado.")

if __name__ == "__main__":
    main()