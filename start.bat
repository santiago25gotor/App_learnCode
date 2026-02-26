@echo off
echo ============================================
echo   PYLEARN - Plataforma de Aprendizaje
echo ============================================
echo.

REM Verificar entorno virtual
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

REM Verificar dependencias
echo [*] Verificando dependencias...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo [!] Instalando dependencias...
    pip install -r requirements.txt
    echo [OK] Dependencias instaladas
    echo.
)

REM Verificar credenciales de Firebase
if not exist "firebase-credentials.json" (
    echo [WARN] No se encontro firebase-credentials.json
    echo.
)

REM Verificar datos locales
if exist "data\lesson_exercises.json" (
    echo [OK] Datos de lecciones encontrados
) else (
    echo [WARN] No se encontraron datos de lecciones
)
echo.

REM Iniciar aplicacion
echo ============================================
echo   [OK] Iniciando servidor...
echo ============================================
echo.
echo   URL: http://localhost:5000
echo   Presiona Ctrl+C para detener
echo.
python app.py

pause