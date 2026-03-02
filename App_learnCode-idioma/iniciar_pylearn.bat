@echo off
title PYLEARN - Python Learning Platform
color 0A
cls

echo.
echo  ============================================================
echo     ██████  ██    ██ ██      ███████  █████  ██████  ███    ██
echo     ██   ██  ██  ██  ██      ██      ██   ██ ██   ██ ████   ██
echo     ██████    ████   ██      █████   ███████ ██████  ██ ██  ██
echo     ██         ██    ██      ██      ██   ██ ██   ██ ██  ██ ██
echo     ██         ██    ███████ ███████ ██   ██ ██   ██ ██   ████
echo  ============================================================
echo              Python Learning Platform  ^|  v1.0
echo  ============================================================
echo.


echo  [1/5] Verificando Python...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  [ERROR] Python no esta instalado o no esta en el PATH.
    echo  Descargalo desde: https://www.python.org/downloads/
    echo  Asegurate de marcar "Add Python to PATH" al instalar.
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VER=%%i
echo  [OK] %PYTHON_VER% detectado

echo.
echo  [2/5] Verificando estructura del proyecto...

if not exist "app.py" (
    echo.
    echo  [ERROR] No se encontro app.py en esta carpeta.
    echo  Asegurate de ejecutar este .bat desde la raiz del proyecto PYLEARN.
    echo.
    pause
    exit /b 1
)
echo  [OK] app.py encontrado


if not exist "firebase-credentials.json" (
    echo.
    echo  [AVISO] No se encontro firebase-credentials.json
    echo  La app puede no funcionar correctamente sin este archivo.
    echo.
)


echo.
echo  [3/5] Verificando dependencias...

pip show flask >nul 2>&1
if %errorlevel% neq 0 (
    echo  [INFO] Instalando dependencias desde requirements.txt...
    echo.
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo.
        echo  [ERROR] Fallo la instalacion de dependencias.
        echo  Ejecuta manualmente: pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
    echo.
    echo  [OK] Dependencias instaladas correctamente
) else (
    echo  [OK] Dependencias ya instaladas
)

echo.
echo  [4/5] Verificando variables de entorno...

if not exist ".env" (
    echo  [INFO] Creando archivo .env con valores por defecto...
    (
        echo FLASK_SECRET_KEY=pylearn-secret-change-in-production
        echo FLASK_ENV=development
        echo FIREBASE_CREDENTIALS_PATH=firebase-credentials.json
        echo SMTP_HOST=smtp.gmail.com
        echo SMTP_PORT=587
        echo SMTP_USER=
        echo SMTP_PASS=
        echo SMTP_FROM=
    ) > .env
    echo  [OK] Archivo .env creado. Edita las credenciales SMTP si necesitas email.
) else (
    echo  [OK] Archivo .env encontrado
)

echo.
echo  [5/5] Iniciando servidor Flask...
echo.
echo  ============================================================
echo   Servidor activo en:  http://127.0.0.1:5000
echo   Pulsa CTRL+C para detener el servidor
echo  ============================================================
echo.


start /b cmd /c "timeout /t 2 /nobreak >nul && start http://127.0.0.1:5000"

python app.py


echo.
echo  ============================================================
echo   El servidor se ha detenido.
echo  ============================================================
echo.
pause
