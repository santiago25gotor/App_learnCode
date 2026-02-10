"""
Script para crear usuario de prueba con todo desbloqueado
Usuario: test@pylearn.com
Contraseña: Test1234
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.firebase_service import FirebaseService

def create_test_user():
    firebase = FirebaseService()
    
    # Credenciales del usuario de prueba
    email = "test@pylearn.com"
    password = "Test1234"
    username = "TestUser"
    
    print("=" * 60)
    print("CREANDO USUARIO DE PRUEBA")
    print("=" * 60)
    print(f"Email: {email}")
    print(f"Contraseña: {password}")
    print(f"Username: {username}")
    print("=" * 60)
    
    # Verificar si ya existe
    if firebase.user_exists(username=username):
        print("[!] El usuario ya existe. Eliminando...")
        # Aquí podrías eliminar el usuario existente si tienes la función
        # firebase.delete_user(username)
    
    # Crear usuario
    success, message, user_id = firebase.create_user(email, password, username)
    
    if not success:
        print(f"[ERROR] Error al crear usuario: {message}")
        return False
    
    print(f"[OK] Usuario creado exitosamente! ID: {user_id}")
    
    # Obtener todas las lecciones
    all_lessons = firebase.get_all_lessons()
    print(f"[INFO] Encontradas {len(all_lessons)} lecciones")
    
    # Marcar todas las lecciones como completadas
    print("[INFO] Desbloqueando todas las lecciones...")
    
    completed_lessons = []
    total_points = 0
    
    for lesson in all_lessons:
        lesson_id = lesson.get('id')
        if lesson_id:
            firebase.mark_lesson_complete(user_id, lesson_id)
            completed_lessons.append(lesson_id)
            total_points += 10  # 10 XP por lección
    
    print(f"[OK] {len(completed_lessons)} lecciones completadas")
    print(f"[PUNTOS] Total de puntos: {total_points} XP")
    
    # Mostrar progreso
    progress = firebase.get_user_progress(user_id)
    print("\n[PROGRESO DEL USUARIO]")
    print(f"   - Lecciones completadas: {len(progress.get('completed_lessons', []))}")
    print(f"   - Puntos totales: {progress.get('total_points', 0)} XP")
    
    print("\n" + "=" * 60)
    print("[EXITO] USUARIO DE PRUEBA CREADO EXITOSAMENTE")
    print("=" * 60)
    print(f"Email: {email}")
    print(f"Contrasena: {password}")
    print(f"Username: {username}")
    print("=" * 60)
    print("\nInicia sesion con estas credenciales en http://localhost:5000")
    print("Todas las lecciones estan desbloqueadas!")
    print("\n")
    
    return True

if __name__ == "__main__":
    create_test_user()
