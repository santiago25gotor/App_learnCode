@echo off
echo ============================================
echo   Python Learning Platform - Inicio
echo ============================================
echo.

REM Verificar si existe el entorno virtual
if not exist "venv" (
    echo [!] No se encontro el entorno virtual
    echo [*] Creando entorno virtual...
    python -m venv venv
    echo [OK] Entorno virtual creado
    echo.
)

REM Activar entorno virtual
echo [*] Activando entorno virtual...
call venv\Scripts\activate.bat

REM Verificar si existen las dependencias
echo [*] Verificando dependencias...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo [!] Instalando dependencias...
    pip install -r requirements.txt
    echo [OK] Dependencias instaladas
    echo.
)

REM Verificar si existe el archivo de credenciales
if not exist "firebase-credentials.json" (
    echo.
    echo ============================================
    echo   [!] ATENCION: Configuracion requerida
    echo ============================================
    echo.
    echo No se encontro el archivo: firebase-credentials.json
    echo.
    echo Por favor:
    echo   1. Ve a Firebase Console
    echo   2. Descarga las credenciales
    echo   3. Guardalo como: firebase-credentials.json
    echo   4. Ejecuta este script de nuevo
    echo.
    echo Guia: GUIA_CONFIGURACION_FIREBASE.md
    echo.
    pause
    exit /b 1
)

REM Verificar si existen lecciones importadas
echo [*] Verificando base de datos...
python -c "from backend.firebase_service import firebase_service; lessons = firebase_service.get_all_lessons(); exit(0 if len(lessons) > 0 else 1)" 2>nul
if errorlevel 1 (
    echo.
    echo [!] No se encontraron lecciones en Firebase
    echo [*] Deseas importar las lecciones ahora? (S/N)
    set /p import_choice=
    if /i "%import_choice%"=="S" (
        python import_lessons.py
    ) else (
        echo [!] Recuerda importar las lecciones con: python import_lessons.py
    )
    echo.
)

REM Iniciar aplicacion
echo ============================================
echo   [OK] Iniciando aplicacion...
echo ============================================
echo.
python app.py

pause