#!/bin/bash

echo "============================================"
echo "  Python Learning Platform - Inicio"
echo "============================================"
echo ""

# Verificar si existe el entorno virtual
if [ ! -d "venv" ]; then
    echo "[!] No se encontró el entorno virtual"
    echo "[*] Creando entorno virtual..."
    python3 -m venv venv
    echo "[OK] Entorno virtual creado"
    echo ""
fi

# Activar entorno virtual
echo "[*] Activando entorno virtual..."
source venv/bin/activate

# Verificar si existen las dependencias
echo "[*] Verificando dependencias..."
if ! pip show flask > /dev/null 2>&1; then
    echo "[!] Instalando dependencias..."
    pip install -r requirements.txt
    echo "[OK] Dependencias instaladas"
    echo ""
fi

# Verificar si existe el archivo de credenciales
if [ ! -f "firebase-credentials.json" ]; then
    echo ""
    echo "============================================"
    echo "  [!] ATENCIÓN: Configuración requerida"
    echo "============================================"
    echo ""
    echo "No se encontró el archivo: firebase-credentials.json"
    echo ""
    echo "Por favor:"
    echo "  1. Ve a Firebase Console"
    echo "  2. Descarga las credenciales"
    echo "  3. Guárdalo como: firebase-credentials.json"
    echo "  4. Ejecuta este script de nuevo"
    echo ""
    echo "Guía: GUIA_CONFIGURACION_FIREBASE.md"
    echo ""
    read -p "Presiona Enter para salir..."
    exit 1
fi

# Verificar si existen lecciones importadas
echo "[*] Verificando base de datos..."
if ! python -c "from backend.firebase_service import firebase_service; lessons = firebase_service.get_all_lessons(); exit(0 if len(lessons) > 0 else 1)" 2>/dev/null; then
    echo ""
    echo "[!] No se encontraron lecciones en Firebase"
    read -p "[*] ¿Deseas importar las lecciones ahora? (S/N): " import_choice
    if [[ "$import_choice" =~ ^[Ss]$ ]]; then
        python import_lessons.py
    else
        echo "[!] Recuerda importar las lecciones con: python import_lessons.py"
    fi
    echo ""
fi

# Iniciar aplicación
echo "============================================"
echo "  [OK] Iniciando aplicación..."
echo "============================================"
echo ""
python app.py

read -p "Presiona Enter para salir..."