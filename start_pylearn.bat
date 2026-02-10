@echo off
REM Script de inicio rapido para PyLearn
REM Verifica e inicia la aplicacion automaticamente

echo ====================================================================
echo     PYLEARN - Plataforma de Aprendizaje de Python
echo ====================================================================
echo.

REM Verificar si el entorno virtual existe
if not exist "venv" (
    echo [!] No se encontro entorno virtual.
    echo [*] Creando entorno virtual...
    python -m venv venv
    echo [OK] Entorno virtual creado.
    echo.
)

REM Activar entorno virtual
echo [*] Activando entorno virtual...
call venv\Scripts\activate.bat

REM Verificar si las dependencias estan instaladas
echo [*] Verificando dependencias...
python -c "import flask" 2>nul
if errorlevel 1 (
    echo [!] Dependencias no encontradas.
    echo [*] Instalando dependencias...
    pip install -r requirements.txt
    echo [OK] Dependencias instaladas.
    echo.
)

REM Verificar credenciales de Firebase
if not exist "firebase-credentials.json" (
    echo [ERROR] No se encontro firebase-credentials.json
    echo.
    echo Por favor, coloca tu archivo de credenciales de Firebase
    echo en la raiz del proyecto con el nombre: firebase-credentials.json
    echo.
    pause
    exit /b 1
)

REM Ejecutar verificacion
echo [*] Ejecutando verificacion de integracion...
python verify_integration.py
if errorlevel 1 (
    echo.
    echo [!] Verificacion fallida. Revisa los mensajes arriba.
    echo.
    pause
    exit /b 1
)

echo.
echo ====================================================================
echo [OK] Todo listo! Iniciando servidor...
echo ====================================================================
echo.
echo Abre tu navegador en: http://localhost:5000
echo.
echo Presiona Ctrl+C para detener el servidor
echo.

REM Iniciar servidor
python app.py
