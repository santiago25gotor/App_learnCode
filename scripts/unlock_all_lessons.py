"""
Script mejorado para crear/actualizar usuario de prueba con todo desbloqueado
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.firebase_service import FirebaseService
import hashlib

def create_or_update_test_user():
    firebase = FirebaseService()
    
    # Credenciales
    email = "demo@pylearn.com"
    password = "Demo1234"
    username = "DemoUser"
    
    print("=" * 60)
    print("CREANDO/ACTUALIZANDO USUARIO DE PRUEBA")
    print("=" * 60)
    print(f"Email: {email}")
    print(f"Contrasena: {password}")
    print(f"Username: {username}")
    print("=" * 60)
    
    # Verificar si existe
    user_id = None
    
    # Intentar por username
    if firebase.user_exists(username=username):
        print("[INFO] Usuario ya existe por username")
        users_ref = firebase.db.collection('usuarios')
        query = users_ref.where('username', '==', username).limit(1)
        docs = query.stream()
        for doc in docs:
            user_id = doc.id
            print(f"[OK] Usuario encontrado: {user_id}")
            break
    
    # Si no, intentar por email
    if not user_id and firebase.user_exists(email=email):
        print("[INFO] Usuario ya existe por email")
        users_ref = firebase.db.collection('usuarios')
        query = users_ref.where('email', '==', email).limit(1)
        docs = query.stream()
        for doc in docs:
            user_id = doc.id
            print(f"[OK] Usuario encontrado: {user_id}")
            break
    
    # Si no existe, crear nuevo
    if not user_id:
        print("[INFO] Creando nuevo usuario...")
        success, message, user_id = firebase.create_user(email, password, username)
        
        if not success:
            print(f"[ERROR] Error al crear usuario: {message}")
            
            # Intentar con otro email
            email = "test123@pylearn.com"
            username = "TestUser123"
            print(f"[INFO] Intentando con {email}...")
            
            success, message, user_id = firebase.create_user(email, password, username)
            
            if not success:
                print(f"[ERROR] Error: {message}")
                return False
        
        print(f"[OK] Usuario creado: {user_id}")
    
    # Obtener todas las lecciones
    all_lessons = firebase.get_all_lessons()
    print(f"\n[INFO] Total de lecciones disponibles: {len(all_lessons)}")
    
    # Marcar TODAS como completadas
    print("[INFO] Marcando TODAS las lecciones como completadas...\n")
    
    completed_count = 0
    for i, lesson in enumerate(all_lessons, 1):
        lesson_id = lesson.get('id')
        titulo = lesson.get('titulo', 'Sin titulo')
        categoria = lesson.get('categoria', 'Sin categoria')
        
        if lesson_id:
            try:
                firebase.mark_lesson_complete(user_id, lesson_id)
                completed_count += 1
                print(f"  [{i}/{len(all_lessons)}] {categoria} - {titulo}")
            except Exception as e:
                print(f"  [ERROR] {titulo}: {str(e)}")
    
    # Obtener progreso final
    progress = firebase.get_user_progress(user_id)
    completed_lessons = progress.get('completed_lessons', [])
    total_points = progress.get('total_points', 0)
    
    print("\n" + "=" * 60)
    print("[EXITO] USUARIO DE PRUEBA LISTO")
    print("=" * 60)
    print(f"Email:      {email}")
    print(f"Contrasena: {password}")
    print(f"Username:   {username}")
    print("=" * 60)
    print(f"Lecciones completadas: {len(completed_lessons)}/{len(all_lessons)}")
    print(f"Puntos totales: {total_points} XP")
    print("=" * 60)
    
    # Agrupar por categoría
    categories = {}
    for lesson in all_lessons:
        cat = lesson.get('categoria', 'Sin categoria')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(lesson)
    
    print("\nDESGLOSE POR CATEGORIA:")
    for cat, lessons in sorted(categories.items()):
        completed_in_cat = sum(1 for l in lessons if l.get('id') in completed_lessons)
        print(f"  {cat}: {completed_in_cat}/{len(lessons)} completadas")
    
    print("\n" + "=" * 60)
    print("Inicia sesion en http://localhost:5000")
    print("TODAS LAS LECCIONES ESTAN DESBLOQUEADAS")
    print("=" * 60 + "\n")
    
    return True

if __name__ == "__main__":
    create_or_update_test_user()
