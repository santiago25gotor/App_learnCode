# 🚀 PYLEARN - Plataforma de Aprendizaje Python

## 📋 USUARIO DE PRUEBA

### Credenciales
```
Email:      demo@pylearn.com
Contraseña: Demo1234
Username:   DemoUser
```

### 🎯 MÉTODO RÁPIDO: Test de Nivel Inicial

La forma más rápida de desbloquear contenido es:

1. **Inicia sesión** con las credenciales de arriba
2. **Ve a**: `http://localhost:5000/placement-test`
3. **Responde el test** (10 preguntas de Python)
4. **Según tus resultados**:
   - ✅ 70%+ en Básico → Desbloquea Python Intermedio
   - ✅ 75%+ en Intermedio → Desbloquea Python Avanzado
   - ✅ 80%+ en Avanzado → Acceso a proyectos especiales

## 🌟 FUNCIONALIDADES PRINCIPALES

### 1. **Landing Page Moderna** (`/`)
- Animaciones dinámicas
- Demo de código interactivo
- Características destacadas
- Dark mode

### 2. **Sistema de Autenticación** (`/login`, `/register`)
- Login con Firebase
- Registro de usuarios
- Sesiones persistentes

### 3. **Dashboard Interactivo** (`/course`)
- Mapa de aprendizaje zigzag
- Lecciones bloqueadas/desbloqueadas
- Progreso visual por categoría
- Sistema de puntos (XP)

### 4. **Lecciones con IDE** (`/lesson/{id}`)
- **Tabs Teoría/Actividades**
- **IDE de Python funcional**
- Ejecución de código en tiempo real
- Terminal integrada
- Atajos de teclado (Ctrl+Enter)
- Modales personalizados (sin alerts nativos)

### 5. **Test de Nivel Inicial** (`/placement-test`)
- 10 preguntas (Básico, Intermedio, Avanzado)
- Timer de 15 minutos
- Sistema de convalidación automático
- Desbloqueo de niveles según resultados

### 6. **Sistema de Exámenes** (`/exam/{category}`)
- Exámenes por categoría
- Preguntas múltiple opción + código
- Timer y barra de progreso
- Pantalla de resultados

### 7. **Página de Perfil** (`/profile`)
- **Estadísticas de progreso**:
  - Puntos totales (XP)
  - Lecciones completadas
  - Progreso por categoría
  - Racha de días
- **Configuración**:
  - Toggle dark mode
  - Notificaciones
  - Sonidos
- **Acciones**:
  - Cambiar contraseña
  - Exportar datos
  - Cerrar sesión

## 🛠️ TECNOLOGÍAS

- **Backend**: Python + Flask
- **Frontend**: HTML, CSS (Vanilla), JavaScript
- **Base de Datos**: Firebase Firestore
- **Autenticación**: Firebase Auth
- **Estilo**: Tailwind CSS
- **Iconos**: Material Symbols
- **Fuentes**: Space Grotesk, JetBrains Mono

## 📁 ESTRUCTURA DEL PROYECTO

```
App_learnCode/
├── app.py                    # Aplicación Flask principal
├── backend/
│   ├── routes.py            # Rutas API
│   ├── firebase_service.py  # Servicio Firebase
│   └── config.py            # Configuración
├── templates/
│   ├── index_new.html       # Landing page
│   ├── login_new.html       # Login/Registro
│   ├── course_new.html      # Dashboard
│   ├── lesson_new.html      # Página de lección con IDE
│   ├── exam.html            # Sistema de exámenes
│   ├── profile.html         # Página de perfil
│   └── placement_test.html  # Test de nivel
├── static/
│   └── js/
│       └── modal-system.js  # Sistema de modales personalizado
├── data/
│   └── lesson_exercises.json # Ejercicios estructurados
└── scripts/
    └── unlock_all_lessons.py # Script de utilidades
```

## 🎨 CARACTERÍSTICAS DE DISEÑO

### ✅ Modales Personalizados
- No usa `alert()` ni `confirm()` nativos
- Modales con animaciones suaves
- 5 tipos: success, error, warning, info, question
- Dark mode compatible

### ✅ Sistema de Ejercicios
- Código inicial vacío (no pre-resuelto)
- Usuario escribe su propia solución
- Instrucciones paso a paso
- Ejemplos de referencia

### ✅ Dark Mode Global
- Persistente con localStorage
- Toggle en todas las páginas
- Colores optimizados

## 🚀 CÓMO USAR

### 1. Iniciar el Servidor
```bash
python app.py
```

### 2. Abrir en Navegador
```
http://localhost:5000
```

### 3. Iniciar Sesión
```
Email: demo@pylearn.com
Contraseña: Demo1234
```

### 4. Probar Funcionalidades

| Función | URL | Descripción |
|---------|-----|-------------|
| Dashboard | `/course` | Ver todas las lecciones |
| Lección | `/lesson/{id}` | IDE con código |
| Test Nivel | `/placement-test` | Convalidar conocimientos |
| Examen | `/exam/Python Básico` | Certificar nivel |
| Perfil | `/profile` | Estadísticas y config |

## 📊 API ENDPOINTS

### Autenticación
- `POST /api/register` - Registrar usuario
- `POST /api/login` - Iniciar sesión
- `POST /api/logout` - Cerrar sesión
- `GET /api/me` - Obtener usuario actual

### Lecciones
- `GET /api/lessons` - Todas las lecciones
- `GET /api/lessons/{id}` - Lección específica
- `POST /api/progress/complete/{id}` - Completar lección

### Código
- `POST /api/execute` - Ejecutar código Python

### Exámenes
- `GET /api/exams/{category}` - Obtener examen
- `POST /api/exams/{id}/submit` - Enviar examen

### Placement Test
- `POST /api/placement-test/submit` - Enviar test de nivel

## 💡 NOTAS IMPORTANTES

### Ejercicios de Calidad
El archivo `data/lesson_exercises.json` contiene:
- **8 ejercicios Python Básico**: Variables, condicionales, bucles, funciones
- **3 ejercicios Python Intermedio**: List comprehensions, lambdas, excepciones
- **2 ejercicios Python Avanzado**: Decoradores, generadores

Cada ejercicio incluye:
- Teoría explicada
- Ejemplo de código
- Instrucciones paso a paso
- Código inicial vacío
- Solución de referencia

### Sistema de Convalidación
El test de nivel permite saltarse contenido conocido:
1. Responde preguntas de los 3 niveles
2. Si apruebas un nivel (70%+), desbloqueas el siguiente
3. Ahorra tiempo y enfócate en lo que necesitas aprender

## 🐛 BUGS CORREGIDOS

✅ Alerts nativos reemplazados por modales  
✅ Código inicial ahora vacío  
✅ Enlace a perfil agregado  
✅ Endpoint `/api/me` creado  
✅ Iconos Material Symbols en todas las páginas  

## 📝 PRÓXIMOS PASOS

- [ ] Implementar guardado real de placement test en Firebase
- [ ] Agregar más ejercicios por categoría
- [ ] Sistema de logros y badges
- [ ] Integrar exámenes con certificados
- [ ] Mejorar sandbox de ejecución de código

---

**¿Preguntas?** Revisa el código o contacta al equipo de desarrollo.
