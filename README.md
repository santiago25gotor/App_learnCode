# PYLEARN - Plataforma de Aprendizaje de Python

Plataforma web interactiva para aprender Python, con editor de codigo integrado, sistema de progreso y busqueda de videos con IA.

## Inicio Rapido

```bash
# Ejecutar directamente
start.bat
```

Abre http://localhost:5000 en tu navegador.

### Credenciales por defecto (modo offline)
- **Email:** `admin@pylearn.com`
- **Password:** cualquiera

## Estructura del Proyecto

```
App_learnCode/
├── app.py                  # Aplicacion Flask principal
├── config.py               # Configuracion centralizada
├── requirements.txt        # Dependencias Python
├── start.bat               # Script de inicio
├── firebase-credentials.json # Credenciales Firebase (gitignored)
│
├── backend/                # Logica del servidor
│   ├── firebase_service.py # Servicio Firebase + modo offline
│   ├── routes.py           # Endpoints de la API
│   └── validators.py       # Validacion de datos
│
├── templates/              # Paginas HTML
│   ├── index_new.html      # Landing page
│   ├── login_new.html      # Login / Registro
│   ├── course_new.html     # Dashboard del curso
│   ├── lesson_new.html     # Vista de leccion + editor
│   ├── n8n.html            # Busqueda de videos con IA
│   ├── exam.html           # Examenes
│   ├── placement_test.html # Test de nivel
│   ├── profile.html        # Perfil de usuario
│   ├── 404_new.html        # Error 404
│   └── 500_new.html        # Error 500
│
├── static/                 # Archivos estaticos
│   └── js/
│       └── modal-system.js # Sistema de modales
│
├── data/                   # Datos de lecciones
│   ├── lesson_exercises.json
│   ├── python_python_basico.csv
│   ├── python_python_intermedio.csv
│   └── python_python_avanzado.csv
│
└── scripts/                # Utilidades
    ├── create_admin.py
    ├── create_test_user.py
    ├── import_lessons.py
    ├── unlock_all_lessons.py
    └── verify_integration.py
```

## Funcionalidades

- **Login/Registro** con Firebase Auth (o modo offline automatico)
- **258 lecciones** de Python (basico, intermedio, avanzado)
- **Editor de codigo** integrado con terminal en cada leccion
- **Busqueda de videos con IA** via n8n + YouTube
- **Sistema de progreso** con XP y lecciones completadas
- **Test de nivel** para saltar contenido conocido
- **Examenes** por categoria
- **Modo oscuro**

## Modo Offline

Si Firebase no esta disponible, la app arranca automaticamente en modo offline:
- Base de datos en memoria con todas las lecciones cargadas desde `data/`
- Login con `admin@pylearn.com` (cualquier password)
- Progreso se guarda en sesion (se pierde al reiniciar)

## API Endpoints

| Metodo | Ruta                            | Descripcion              |
|--------|---------------------------------|--------------------------|
| POST   | `/api/login`                    | Iniciar sesion          |
| POST   | `/api/register`                 | Registrar usuario       |
| POST   | `/api/logout`                   | Cerrar sesion           |
| GET    | `/api/me`                       | Usuario actual          |
| GET    | `/api/lessons`                  | Listar lecciones        |
| GET    | `/api/lessons/<id>`             | Detalle de leccion      |
| GET    | `/api/search?q=`                | Buscar lecciones        |
| POST   | `/api/execute`                  | Ejecutar codigo Python  |
| POST   | `/api/progress/complete/<id>`   | Completar leccion       |
| GET    | `/api/health`                   | Estado de la API        |
