"""
Script para crear un usuario admin con todo el temario desbloqueado.
Ejecutar una sola vez para configurar el admin.

Uso: python create_admin.py
"""
import os
import sys
import io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config

def create_admin():
    """Crear usuario admin con todo desbloqueado"""
    
    # Importar Firebase
    try:
        from backend.firebase_service import firebase_service
        from firebase_admin import auth, firestore
    except Exception as e:
        print(f"[ERROR] Error al conectar con Firebase: {e}")
        print("   Asegurate de que las credenciales de Firebase estan configuradas.")
        return False
    
    # Configuracion del admin
    ADMIN_EMAIL = "admin@pylearn.com"
    ADMIN_PASSWORD = "Admin123!"
    ADMIN_USERNAME = "admin"
    
    print("=" * 50)
    print("PYLEARN - Crear Usuario Admin")
    print("=" * 50)
    print(f"   Email:    {ADMIN_EMAIL}")
    print(f"   Username: {ADMIN_USERNAME}")
    print(f"   Password: {ADMIN_PASSWORD}")
    print("=" * 50)
    
    # 1. Verificar si el admin ya existe
    try:
        existing_user = auth.get_user_by_email(ADMIN_EMAIL)
        print(f"\n[!] El usuario admin ya existe (UID: {existing_user.uid})")
        print("   Actualizando progreso...")
        admin_uid = existing_user.uid
    except auth.UserNotFoundError:
        # Crear el usuario
        print("\n[*] Creando usuario admin en Firebase Auth...")
        try:
            user = auth.create_user(
                email=ADMIN_EMAIL,
                password=ADMIN_PASSWORD,
                display_name=ADMIN_USERNAME
            )
            admin_uid = user.uid
            print(f"   [OK] Usuario creado (UID: {admin_uid})")
        except Exception as e:
            print(f"   [ERROR] Error al crear usuario: {e}")
            return False
    
    # 2. Obtener todas las lecciones
    print("\n[*] Obteniendo todas las lecciones...")
    all_lessons = firebase_service.get_all_lessons()
    lesson_ids = [lesson['id'] for lesson in all_lessons]
    total_lessons = len(lesson_ids)
    total_points = total_lessons * 10
    
    print(f"   Lecciones encontradas: {total_lessons}")
    
    for lesson in all_lessons:
        cat = lesson.get('categoria', 'Sin categoria')
        titulo = lesson.get('titulo', 'Sin titulo')
        print(f"      - [{cat}] {titulo} (ID: {lesson['id']})")
    
    # 3. Crear/actualizar documento en Firestore
    print("\n[*] Guardando datos en Firestore...")
    db = firebase_service.db
    
    user_data = {
        'username': ADMIN_USERNAME,
        'email': ADMIN_EMAIL,
        'created_at': firestore.SERVER_TIMESTAMP,
        'is_admin': True,
        'progress': {
            'completed_lessons': lesson_ids,
            'current_level': 'Python Avanzado',
            'total_points': total_points,
            'placement_test_completed': True,
            'unlocked_categories': ['Python Básico', 'Python Intermedio', 'Python Avanzado'],
            'placement_test': {
                'scores': {
                    'basic': 100,
                    'intermediate': 100,
                    'advanced': 100
                },
                'completed_at': firestore.SERVER_TIMESTAMP
            }
        }
    }
    
    try:
        db.collection(Config.USERS_COLLECTION).document(admin_uid).set(user_data)
        print("   [OK] Datos guardados correctamente")
    except Exception as e:
        print(f"   [ERROR] Error al guardar datos: {e}")
        return False
    
    # 4. Resumen
    print("\n" + "=" * 50)
    print("[OK] Usuario admin creado exitosamente!")
    print("=" * 50)
    print(f"   Email:     {ADMIN_EMAIL}")
    print(f"   Username:  {ADMIN_USERNAME}")
    print(f"   Password:  {ADMIN_PASSWORD}")
    print(f"   UID:       {admin_uid}")
    print(f"   Lecciones: {total_lessons} completadas")
    print(f"   Puntos:    {total_points} XP")
    print(f"   Nivel:     Python Avanzado")
    print("=" * 50)
    print("\nPuedes iniciar sesion con estas credenciales.")
    print("   Las credenciales tambien se guardan en ADMIN_CREDENTIALS.txt")
    
    # 5. Guardar credenciales en archivo
    with open('ADMIN_CREDENTIALS.txt', 'w', encoding='utf-8') as f:
        f.write("=" * 40 + "\n")
        f.write("PYLEARN - Credenciales Admin\n")
        f.write("=" * 40 + "\n")
        f.write(f"Email:    {ADMIN_EMAIL}\n")
        f.write(f"Username: {ADMIN_USERNAME}\n")
        f.write(f"Password: {ADMIN_PASSWORD}\n")
        f.write(f"UID:      {admin_uid}\n")
        f.write(f"Puntos:   {total_points} XP\n")
        f.write(f"Nivel:    Python Avanzado\n")
        f.write(f"Lecciones completadas: {total_lessons}\n")
        f.write("=" * 40 + "\n")
    
    return True


if __name__ == '__main__':
    success = create_admin()
    if not success:
        print("\n[ERROR] No se pudo crear el usuario admin.")
        sys.exit(1)
