# 🐍 PYLEARN

**Plataforma interactiva de aprendizaje de Python** con sistema de gamificación, ejecución de código en tiempo real y rutas de aprendizaje progresivas.

---

## 📋 Índice

- [Descripción](#descripción)
- [Características](#características)
- [Stack tecnológico](#stack-tecnológico)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Instalación](#instalación)
- [Variables de entorno](#variables-de-entorno)
- [API Reference](#api-reference)
- [Sistema de lecciones](#sistema-de-lecciones)
- [Roles y permisos](#roles-y-permisos)

---

## Descripción

PYLEARN es una aplicación web full-stack diseñada para aprender Python de forma progresiva y gamificada. Los usuarios avanzan a través de más de **1.700 lecciones** organizadas en tres niveles, ganan XP al completar ejercicios, y pueden ejecutar código Python directamente en el navegador.

El sistema incluye un **test de nivel inicial** (placement test) que detecta los conocimientos previos del usuario y desbloquea automáticamente el nivel correspondiente, evitando que tenga que empezar desde cero si ya tiene experiencia.

---

## Características

### Para el alumno
- **Ruta de aprendizaje visual** — mapa tipo juego que muestra el progreso de forma gráfica
- **Temario estructurado** — vista de syllabus con lecciones organizadas por categoría
- **Ejecución de código en tiempo real** — sandbox Python seguro integrado en cada lección
- **Sistema de XP y rachas** — puntos por lección completada y racha de días consecutivos
- **Exámenes por categoría** — evaluación al finalizar cada nivel
- **Test de nivel inicial** — placement test para usuarios con conocimientos previos
- **Buscador de lecciones** — búsqueda por título y contenido en tiempo real
- **Videos IA** — generación de vídeos educativos con n8n + YouTube
- **Perfil personalizable** — avatar, estadísticas de aprendizaje, exportación de datos

### Para el administrador
- **Panel de administración** — gestión de usuarios, estadísticas globales
- **Control de progreso** — desbloquear o resetear lecciones por usuario
- **Gestión de roles** — asignación de rol admin/user
- **Importación masiva de lecciones** — mediante CSV

---

## Stack tecnológico

### Backend
| Tecnología | Uso |
|---|---|
| **Python / Flask** | Framework web, API REST |
| **Firebase Admin SDK** | Autenticación, base de datos (Firestore) |
| **Cloudinary** | Almacenamiento de avatares de usuario |
| **smtplib (Gmail SMTP)** | Envío de códigos de verificación por email |

### Frontend
| Tecnología | Uso |
|---|---|
| **Tailwind CSS** (CDN) | Estilos y diseño responsive |
| **Space Grotesk / JetBrains Mono** | Tipografías |
| **Material Symbols** | Iconografía |
| **Vanilla JS** | Lógica del cliente |

### Integraciones externas
| Servicio | Uso |
|---|---|
| **Firebase / Firestore** | Persistencia de datos de usuarios y progreso |
| **Firebase Auth** | Autenticación con Google OAuth |
| **Cloudinary** | CDN para imágenes de perfil |
| **n8n** | Automatización para generación de vídeos educativos con YouTube |

---

## Estructura del proyecto

```
pylearn/
│
├── backend/
│   ├── core/
│   │   ├── firebase.py              # Servicio Firebase (singleton)
│   │   └── verification_service.py  # Generación y validación de códigos OTP
│   │
│   ├── routes/
│   │   ├── auth_routes.py           # /api/auth — registro, login, contraseña
│   │   ├── user_routes.py           # /api/user — perfil, avatar, placement test
│   │   ├── lesson_routes.py         # /api/lessons — lecciones, búsqueda, completar
│   │   ├── code_routes.py           # /api/code — ejecución de código, exámenes
│   │   └── admin_routes.py          # /api/admin — gestión de usuarios y stats
│   │
│   └── utils/
│       ├── decorators.py            # @login_required
│       └── validators.py            # Validación de passwords y emails
│
├── static/
│   └── js/
│       ├── modal-system.js          # Sistema de modales reutilizable
│       └── search-system.js         # Buscador de lecciones
│
├── templates/
│   ├── index_new.html               # Landing page
│   ├── login_new.html               # Login / Registro
│   ├── course_new.html              # Ruta de aprendizaje + Temario
│   ├── lesson_new.html              # Lección individual + editor de código
│   ├── profile.html                 # Perfil de usuario
│   ├── placement_test.html          # Test de nivel inicial
│   ├── exam.html                    # Examen por categoría
│   ├── admin.html                   # Panel de administración
│   ├── 404_new.html                 # Error 404
│   └── 500_new.html                 # Error 500
│
├── tools/
│   ├── import_lessons.py            # Importación de lecciones desde CSV
│   ├── manage_users.py              # Gestión de usuarios por CLI
│   └── verify_integration.py        # Verificación de integraciones externas
│
└── data/
    ├── python_basico.csv            # 762 lecciones de nivel básico
    ├── python_intermedio.csv        # 580 lecciones de nivel intermedio
    ├── python_avanzado.csv          # 423 lecciones de nivel avanzado
    └── pylearn_lecciones.csv        # Dataset combinado (1.765 lecciones)
```

---

## Instalación

### Requisitos previos
- Python 3.9+
- Cuenta de Firebase con Firestore habilitado
- Cuenta de Cloudinary
- Cuenta de Gmail con contraseña de aplicación (para SMTP)

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/pylearn.git
cd pylearn

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales (ver sección Variables de entorno)

# 5. Importar lecciones a Firestore
python tools/import_lessons.py --file data/pylearn_lecciones.csv

# 6. Arrancar el servidor
flask run
```

La aplicación estará disponible en `http://localhost:5000`.

---

## Variables de entorno

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
# Flask
SECRET_KEY=tu_clave_secreta_flask
FLASK_ENV=development

# Firebase
FIREBASE_CREDENTIALS=ruta/a/tu/serviceAccountKey.json

# Cloudinary
CLOUDINARY_CLOUD_NAME=tu_cloud_name
CLOUDINARY_API_KEY=tu_api_key
CLOUDINARY_API_SECRET=tu_api_secret

# SMTP (Gmail)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu_email@gmail.com
SMTP_PASS=tu_contraseña_de_aplicacion
SMTP_FROM=tu_email@gmail.com
```

> **Nota:** Para Gmail, necesitas generar una [contraseña de aplicación](https://support.google.com/accounts/answer/185833) en tu cuenta de Google, no usar tu contraseña normal.

---

## API Reference

### Autenticación — `/api/auth`

| Método | Endpoint | Descripción |
|---|---|---|
| `POST` | `/send-code` | Enviar código OTP de verificación al email |
| `POST` | `/register` | Registro de nuevo usuario |
| `POST` | `/login` | Login con email y contraseña |
| `POST` | `/logout` | Cerrar sesión |
| `POST` | `/change-password` | Cambiar contraseña |
| `POST` | `/forgot-password/send-code` | Recuperación de contraseña — enviar código |
| `POST` | `/forgot-password/reset` | Recuperación de contraseña — nueva contraseña |
| `POST` | `/google` | Login con Google OAuth |

### Usuario — `/api/user`

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/me` | Obtener perfil completo del usuario autenticado |
| `PUT` | `/avatar` | Actualizar avatar de perfil |
| `POST` | `/placement-test/submit` | Enviar resultados del test de nivel |

### Lecciones — `/api/lessons`

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/` | Obtener todas las lecciones |
| `GET` | `/<lesson_id>` | Obtener una lección por ID |
| `GET` | `/categories` | Obtener categorías disponibles |
| `GET` | `/search?q=<query>` | Buscar lecciones por texto |
| `POST` | `/complete/<lesson_id>` | Marcar lección como completada |
| `GET` | `/health` | Health check del servicio |

### Código y exámenes — `/api/code`

| Método | Endpoint | Descripción |
|---|---|---|
| `POST` | `/execute` | Ejecutar código Python en sandbox |
| `GET` | `/exams/<category>` | Obtener examen de una categoría |
| `POST` | `/exams/<exam_id>/submit` | Enviar respuestas de un examen |

### Administración — `/api/admin`

| Método | Endpoint | Descripción | Requiere |
|---|---|---|---|
| `GET` | `/stats` | Estadísticas globales de la plataforma | Admin |
| `GET` | `/users` | Listar todos los usuarios | Admin |
| `GET` | `/users/<id>` | Detalle de un usuario | Admin |
| `PUT` | `/users/<id>/role` | Cambiar rol de usuario | Admin |
| `POST` | `/users/<id>/unlock` | Desbloquear lecciones de un usuario | Admin |
| `POST` | `/users/<id>/reset` | Resetear progreso de un usuario | Admin |
| `DELETE` | `/users/<id>` | Eliminar usuario | Admin |
| `GET` | `/check` | Verificar si el usuario actual es admin | Auth |

---

## Sistema de lecciones

### Niveles y desblogueo

El contenido está dividido en tres niveles. Por defecto, solo **Python Básico** está disponible al registrarse. Los niveles siguientes se desbloquean al completar las lecciones del nivel anterior, o automáticamente mediante el **placement test**.

| Nivel | Lecciones | Desbloqueo |
|---|---|---|
| 🎯 Python Básico | 15 | Al registrarse |
| ⚡ Python Intermedio | 9 | Al completar Básico o placement test ≥ 70 en básico |
| 🚀 Python Avanzado | 6 | Al completar Intermedio o placement test ≥ 75 en intermedio |

### Placement Test

El test de nivel evalúa los conocimientos previos del usuario con una puntuación total de 0 a 100:

- **≤ 50 puntos** → Nivel Básico (inicio normal)
- **51–79 puntos** → Nivel Intermedio (se desbloquea Básico completo + acceso a Intermedio)
- **≥ 80 puntos** → Nivel Avanzado (se desbloquean Básico e Intermedio completos + acceso a Avanzado)

### Importar lecciones desde CSV

```bash
python tools/import_lessons.py --file data/python_basico.csv
python tools/import_lessons.py --file data/python_intermedio.csv
python tools/import_lessons.py --file data/python_avanzado.csv
```

Formato esperado del CSV:
```
numero_leccion, titulo, url, descripcion, ejemplos_codigo, categoria
```

---

## Roles y permisos

| Rol | Acceso |
|---|---|
| `user` | Lecciones, perfil, exámenes, placement test |
| `admin` | Todo lo anterior + panel de administración completo |

Para crear el primer usuario admin mediante CLI:

```bash
python tools/manage_users.py --email admin@ejemplo.com --role admin
```

---

## Licencia

Este proyecto es privado. Todos los derechos reservados.
