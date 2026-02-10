"""
Script de verificacion para la integracion del frontend con Firebase
Verifica que todos los componentes esten correctamente configurados
"""
import os
import sys

def check_file(filepath, description):
    """Verificar si un archivo existe"""
    if os.path.exists(filepath):
        print(f"  [OK] {description}")
        return True
    else:
        print(f"  [FALTA] {description} - No encontrado: {filepath}")
        return False

def main():
    print("=" * 70)
    print("VERIFICACION DE INTEGRACION PYLEARN")
    print("=" * 70)
    print()
    
    all_ok = True
    
    # Verificar archivos principales
    print("Archivos principales:")
    all_ok &= check_file("app.py", "Aplicacion Flask principal")
    all_ok &= check_file("config.py", "Archivo de configuracion")
    all_ok &= check_file("requirements.txt", "Dependencias Python")
    all_ok &= check_file("firebase-credentials.json", "Credenciales de Firebase")
    print()
    
    # Verificar backend
    print("Backend (API):")
    all_ok &= check_file("backend/routes.py", "Rutas de la API")
    all_ok &= check_file("backend/firebase_service.py", "Servicio de Firebase")
    all_ok &= check_file("backend/validators.py", "Validadores")
    print()
    
    # Verificar nuevas plantillas
    print("Plantillas HTML (Nuevas):")
    all_ok &= check_file("templates/index_new.html", "Landing page")
    all_ok &= check_file("templates/login_new.html", "Login/Registro integrado")
    all_ok &= check_file("templates/course_new.html", "Dashboard principal")
    all_ok &= check_file("templates/lesson_new.html", "Vista de leccion con IDE")
    all_ok &= check_file("templates/404_new.html", "Pagina de error 404")
    all_ok &= check_file("templates/500_new.html", "Pagina de error 500")
    print()
    
    # Verificar datos
    print("Archivos de datos:")
    check_file("data/python_python_básico.csv", "Lecciones basicas")
    check_file("data/python_python_intermedio.csv", "Lecciones intermedias")
    check_file("data/python_python_avanzado.csv", "Lecciones avanzadas")
    print()
    
    # Verificar documentación
    print("Documentacion:")
    all_ok &= check_file("INTEGRATION_README.md", "Documentacion de integracion")
    print()
    
    # Verificar imports de Python
    print("Verificando imports de Python:")
    try:
        import flask
        print("  [OK] Flask instalado")
    except ImportError:
        print("  [ERROR] Flask NO instalado")
        all_ok = False
    
    try:
        import firebase_admin
        print("  [OK] Firebase Admin instalado")
    except ImportError:
        print("  [ERROR] Firebase Admin NO instalado")
        all_ok = False
    
    try:
        from flask_cors import CORS
        print("  [OK] Flask-CORS instalado")
    except ImportError:
        print("  [ERROR] Flask-CORS NO instalado")
        all_ok = False
    
    print()
    
    # Resultado final
    print("=" * 70)
    if all_ok:
        print("VERIFICACION EXITOSA! Todos los componentes estan en su lugar.")
        print()
        print("Proximos pasos:")
        print("  1. Asegurate de que Firebase este configurado correctamente")
        print("  2. Importa las lecciones con: python import_lessons.py")
        print("  3. Ejecuta el servidor con: python app.py")
        print("  4. Abre tu navegador en: http://localhost:5000")
    else:
        print("VERIFICACION FALLIDA - Faltan algunos componentes")
        print()
        print("Acciones recomendadas:")
        print("  1. Revisa los archivos faltantes arriba")
        print("  2. Instala las dependencias: pip install -r requirements.txt")
        print("  3. Verifica que firebase-credentials.json este presente")
    print("=" * 70)
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
