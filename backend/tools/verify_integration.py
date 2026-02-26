import os
import sys

def check_file(filepath, description):
    
    if os.path.exists(filepath):
        print(f"  [OK] {description}")
        return True
    else:
        print(f"  [FALTA] {description} - No encontrado: {filepath}")
        return False

def main():
    print("=" * 70)
    print("VERIFICACIÓN DE INTEGRACIÓN PYLEARN - NUEVA ESTRUCTURA")
    print("=" * 70)
    print()
    
    all_ok = True
    
    print("📂 Archivos principales:")
    all_ok &= check_file("app.py", "Aplicación Flask principal")
    all_ok &= check_file("config.py", "Archivo de configuración")
    all_ok &= check_file("requirements.txt", "Dependencias Python")
    all_ok &= check_file("firebase-credentials.json", "Credenciales de Firebase")
    print()
    
   
    print("🔌 Módulos de la API (Blueprints):")
    all_ok &= check_file("api/auth_routes.py", "Módulo de Autenticación")
    all_ok &= check_file("api/user_routes.py", "Módulo de Usuario/Progreso")
    all_ok &= check_file("api/lesson_routes.py", "Módulo de Lecciones")
    all_ok &= check_file("api/code_routes.py", "Módulo de Ejecución de Código")
    all_ok &= check_file("core/firebase.py", "Servicio Central de Firebase")
    print()
    
    print("🛠️  Utilidades y Herramientas:")
    all_ok &= check_file("utils/validators.py", "Validadores de datos")
    all_ok &= check_file("utils/decorators.py", "Decoradores (login_required)")
    all_ok &= check_file("tools/manage_users.py", "Nueva herramienta de gestión de usuarios")
    all_ok &= check_file("tools/import_lessons.py", "Importador de lecciones")
    print()
    
    print("🖼️  Plantillas HTML:")
    templates = [
        ("templates/index_new.html", "Landing page"),
        ("templates/login_new.html", "Login/Registro"),
        ("templates/course_new.html", "Dashboard"),
        ("templates/lesson_new.html", "IDE de lecciones"),
        ("templates/profile.html", "Perfil de usuario")
    ]
    for path, desc in templates:
        all_ok &= check_file(path, desc)
    print()

    print("📦 Librerías de Python:")
    dependencies = ["flask", "firebase_admin", "flask_cors", "pandas"]
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"  [OK] {dep} instalado")
        except ImportError:
            print(f"  [ERROR] {dep} NO instalado")
            all_ok = False
    print()
    
    print("=" * 70)
    if all_ok:
        print("✅ VERIFICACIÓN EXITOSA: La nueva estructura es correcta.")
        print("\nPróximos pasos recomendados:")
        print("  1. Ejecuta: python tools/import_lessons.py (para cargar contenido)")
        print("  2. Ejecuta: python tools/manage_users.py --action create --role admin ...")
        print("  3. Lanza el servidor: python app.py")
    else:
        print("❌ VERIFICACIÓN FALLIDA: Revisa los componentes que faltan.")
        print("\nNota: Asegúrate de haber renombrado la carpeta 'scripts' a 'tools'.")
    print("=" * 70)
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())