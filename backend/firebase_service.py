"""
Servicio de conexion y operaciones con Firebase
Incluye modo offline de respaldo cuando Firebase no esta disponible
"""
import firebase_admin
from firebase_admin import credentials, firestore, auth
from config import Config
import os
import json


class FirebaseService:
    """Servicio singleton para manejar la conexion con Firebase"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Patron Singleton - solo una instancia de Firebase"""
        if cls._instance is None:
            cls._instance = super(FirebaseService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializar la conexion con Firebase"""
        if not FirebaseService._initialized:
            self._initialize_firebase()
            FirebaseService._initialized = True
    
    def _initialize_firebase(self):
        self.db = None
        self.offline_mode = False
        self.mock_db = {
            'users': {
                'offline_admin': {
                    'username': 'admin',
                    'email': 'admin@pylearn.com',
                    'role': 'admin',
                    'progress': {
                        'total_points': 0,
                        'completed_lessons': [],
                        'unlocked_categories': ['Python Básico', 'Python Intermedio', 'Python Avanzado'],
                        'placement_test_completed': True
                    }
                }
            },
            'lessons': {}
        }
        # Load lessons from local JSON/CSV for offline mode
        self._load_local_lessons()
        self._connect_firebase()

    def _load_local_lessons(self):
        """Cargar lecciones desde archivos locales para modo offline"""
        try:
            exercises_path = os.path.join('data', 'lesson_exercises.json')
            if os.path.exists(exercises_path):
                with open(exercises_path, 'r', encoding='utf-8') as f:
                    exercises_data = json.load(f)
                
                lesson_counter = 1
                category_map = {
                    'python_basico': 'Python Básico',
                    'python_intermedio': 'Python Intermedio',
                    'python_avanzado': 'Python Avanzado'
                }
                for category_key, lessons_list in exercises_data.items():
                    cat_name = category_map.get(category_key, category_key)
                    if isinstance(lessons_list, list):
                        for i, lesson in enumerate(lessons_list):
                            lesson_id = lesson.get('id', f'lesson_{lesson_counter}')
                            self.mock_db['lessons'][lesson_id] = {
                                'id': lesson_id,
                                'titulo': lesson.get('title', f'Leccion {lesson_counter}'),
                                'descripcion': lesson.get('theory', ''),
                                'categoria': cat_name,
                                'numero_leccion': lesson_counter,
                                'ejemplos_codigo': lesson.get('example', ''),
                                'video_url': '',
                                'url': ''
                            }
                            lesson_counter += 1
            
            # Also try loading from CSV files
            import csv
            csv_files = {
                'Python Básico': 'data/python_python_básico.csv',
                'Python Intermedio': 'data/python_python_intermedio.csv',
                'Python Avanzado': 'data/python_python_avanzado.csv',
            }
            lesson_counter = 1
            for cat_name, csv_path in csv_files.items():
                if os.path.exists(csv_path):
                    with open(csv_path, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            lesson_id = row.get('id', f'csv_{cat_name}_{lesson_counter}')
                            # Only add if not already present
                            if lesson_id not in self.mock_db['lessons']:
                                self.mock_db['lessons'][lesson_id] = {
                                    'id': lesson_id,
                                    'titulo': row.get('titulo', row.get('title', f'Leccion {lesson_counter}')),
                                    'descripcion': row.get('descripcion', row.get('description', '')),
                                    'categoria': cat_name,
                                    'numero_leccion': int(row.get('numero_leccion', lesson_counter)),
                                    'ejemplos_codigo': row.get('ejemplos_codigo', row.get('code', '')),
                                    'video_url': row.get('video_url', ''),
                                    'url': row.get('url', '')
                                }
                            lesson_counter += 1
                            
            print(f"[INFO] Lecciones locales cargadas: {len(self.mock_db['lessons'])}")
        except Exception as e:
            print(f"[WARN] No se pudieron cargar lecciones locales: {e}")

    def _connect_firebase(self):
        """Intentar conectar a Firebase con timeout"""
        import threading
        
        cred_path = Config.FIREBASE_CREDENTIALS
        if not os.path.exists(cred_path):
            print(f"[ERROR] No se encontro {cred_path}")
            print("[WARN] ACTIVANDO MODO OFFLINE")
            self.offline_mode = True
            return
        
        # Use a thread with timeout to prevent hanging
        result = {'success': False, 'error': None}
        
        def try_connect():
            try:
                if not len(firebase_admin._apps):
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred)
                
                db = firestore.client()
                # Quick test - this is what hangs on some Windows setups
                list(db.collection('users').limit(1).stream())
                result['success'] = True
                result['db'] = db
            except Exception as e:
                result['error'] = str(e)
        
        # Try connecting with a 10-second timeout
        thread = threading.Thread(target=try_connect)
        thread.daemon = True
        thread.start()
        thread.join(timeout=10)  # Wait max 10 seconds
        
        if result['success']:
            self.db = result.get('db')
            self.offline_mode = False
            print("[OK] Firebase conectado correctamente")
        else:
            error_msg = result.get('error', 'Timeout - conexion demasiado lenta')
            print(f"[ERROR] Firebase no disponible: {error_msg}")
            print("[WARN] ACTIVANDO MODO OFFLINE (Base de datos en memoria)")
            self.offline_mode = True
    
    # ============================================
    # OPERACIONES DE AUTENTICACION
    # ============================================
    
    def create_user(self, email, password, username):
        """Crear un nuevo usuario"""
        if self.offline_mode:
            import hashlib
            uid = hashlib.md5(email.encode()).hexdigest()[:20]
            self.mock_db['users'][uid] = {
                'username': username,
                'email': email,
                'role': 'user',
                'progress': {
                    'completed_lessons': [],
                    'current_level': 'Python Básico',
                    'total_points': 0,
                    'unlocked_categories': ['Python Básico'],
                    'placement_test_completed': False
                }
            }
            return True, "Usuario registrado (modo offline)", uid
        
        try:
            user = auth.create_user(
                email=email,
                password=password,
                display_name=username
            )
            
            self.db.collection(Config.USERS_COLLECTION).document(user.uid).set({
                'username': username,
                'email': email,
                'created_at': firestore.SERVER_TIMESTAMP,
                'progress': {
                    'completed_lessons': [],
                    'current_level': 'Python Básico',
                    'total_points': 0
                }
            })
            
            return True, "Usuario registrado exitosamente", user.uid
            
        except auth.EmailAlreadyExistsError:
            return False, "El email ya esta registrado", None
        except Exception as e:
            return False, f"Error al crear usuario: {str(e)}", None
    
    def verify_user(self, email, password):
        """Verificar credenciales de usuario"""
        if self.offline_mode:
            for uid, user in self.mock_db['users'].items():
                if user['email'] == email:
                    return True, "Login exitoso (modo offline)", {**user, 'uid': uid}
            return False, "Usuario no encontrado", None

        try:
            user = auth.get_user_by_email(email)
            user_doc = self.db.collection(Config.USERS_COLLECTION).document(user.uid).get()
            
            if user_doc.exists:
                user_data = user_doc.to_dict()
                user_data['uid'] = user.uid
                return True, "Login exitoso", user_data
            else:
                return False, "Usuario no encontrado en la base de datos", None
                
        except auth.UserNotFoundError:
            return False, "Email no registrado", None
        except Exception as e:
            return False, f"Error al verificar usuario: {str(e)}", None
    
    def get_user_by_username(self, username):
        """Buscar usuario por nombre de usuario"""
        if self.offline_mode:
            for uid, user in self.mock_db['users'].items():
                if user.get('username') == username:
                    return {**user, 'uid': uid}
            return None
        
        try:
            users = self.db.collection(Config.USERS_COLLECTION).where(
                'username', '==', username
            ).limit(1).get()
            
            if users:
                user_data = users[0].to_dict()
                user_data['uid'] = users[0].id
                return user_data
            return None
            
        except Exception as e:
            print(f"Error al buscar usuario: {str(e)}")
            return None
    
    def user_exists(self, username=None, email=None):
        """Verificar si un usuario o email ya existe"""
        if self.offline_mode:
            for uid, user in self.mock_db['users'].items():
                if username and user.get('username') == username:
                    return True
                if email and user.get('email') == email:
                    return True
            return False
        
        try:
            if username:
                return self.get_user_by_username(username) is not None
            
            if email:
                try:
                    auth.get_user_by_email(email)
                    return True
                except auth.UserNotFoundError:
                    return False
            
            return False
            
        except Exception as e:
            print(f"Error al verificar existencia: {str(e)}")
            return False
    
    # ============================================
    # OPERACIONES DE LECCIONES
    # ============================================
    
    def add_lesson(self, lesson_data):
        """Agregar una leccion a Firestore"""
        if self.offline_mode:
            lesson_id = f"offline_{len(self.mock_db['lessons']) + 1}"
            lesson_data['id'] = lesson_id
            self.mock_db['lessons'][lesson_id] = lesson_data
            return True, "Leccion agregada (offline)", lesson_id
        
        try:
            doc_ref = self.db.collection(Config.LESSONS_COLLECTION).add(lesson_data)
            return True, "Leccion agregada exitosamente", doc_ref[1].id
        except Exception as e:
            return False, f"Error al agregar leccion: {str(e)}", None
    
    def get_lessons_by_category(self, category):
        """Obtener lecciones por categoria"""
        if self.offline_mode:
            results = []
            for lid, lesson in self.mock_db['lessons'].items():
                if lesson.get('categoria', '').lower().replace('á', 'a').replace('é', 'e').replace('í', 'i') == category.lower().replace('á', 'a').replace('é', 'e').replace('í', 'i'):
                    results.append({**lesson, 'id': lid})
            results.sort(key=lambda x: x.get('numero_leccion', 0))
            return results
        
        try:
            lessons = self.db.collection(Config.LESSONS_COLLECTION).where(
                'categoria', '==', category
            ).order_by('numero_leccion').get()
            
            return [
                {**lesson.to_dict(), 'id': lesson.id}
                for lesson in lessons
            ]
        except Exception as e:
            print(f"Error al obtener lecciones: {str(e)}")
            return []
    
    def get_all_lessons(self):
        """Obtener todas las lecciones"""
        if self.offline_mode:
            results = []
            for lid, lesson in self.mock_db['lessons'].items():
                results.append({**lesson, 'id': lid})
            results.sort(key=lambda x: x.get('numero_leccion', 0))
            return results
        
        try:
            lessons = self.db.collection(Config.LESSONS_COLLECTION).order_by(
                'numero_leccion'
            ).get()
            
            return [
                {**lesson.to_dict(), 'id': lesson.id}
                for lesson in lessons
            ]
        except Exception as e:
            print(f"Error al obtener lecciones: {str(e)}")
            return []
    
    def get_lesson_by_id(self, lesson_id):
        """Obtener una leccion especifica"""
        if self.offline_mode:
            lesson = self.mock_db['lessons'].get(lesson_id)
            if lesson:
                return {**lesson, 'id': lesson_id}
            return None
        
        try:
            lesson = self.db.collection(Config.LESSONS_COLLECTION).document(lesson_id).get()
            if lesson.exists:
                return {**lesson.to_dict(), 'id': lesson.id}
            return None
        except Exception as e:
            print(f"Error al obtener leccion: {str(e)}")
            return None
        
    def search_lessons(self, query):
        """Buscar lecciones por texto"""
        if self.offline_mode:
            query = query.lower().strip()
            if not query:
                return []
            results = []
            for lid, lesson in self.mock_db['lessons'].items():
                searchable = ' '.join([
                    str(lesson.get('titulo', '')),
                    str(lesson.get('descripcion', '')),
                    str(lesson.get('ejemplos_codigo', '')),
                    str(lesson.get('categoria', ''))
                ]).lower()
                if query in searchable:
                    results.append({**lesson, 'id': lid})
            results.sort(key=lambda x: (
                query not in str(x.get('titulo', '')).lower(),
                x.get('numero_leccion', 0)
            ))
            return results
        
        try:
            query = query.lower().strip()
            if not query:
                return []

            lessons = self.db.collection(Config.LESSONS_COLLECTION).get()
            results = []

            for lesson in lessons:
                data = lesson.to_dict()
                searchable_text = " ".join([
                    str(data.get("titulo", "")),
                    str(data.get("descripcion", "")),
                    str(data.get("ejemplos_codigo", "")),
                    str(data.get("categoria", ""))
                ]).lower()

                if query in searchable_text:
                    results.append({**data, "id": lesson.id})

            results.sort(key=lambda x: (
                query not in str(x.get("titulo", "")).lower(),
                x.get("numero_leccion", 0)
            ))

            return results

        except Exception as e:
            print(f"[ERROR] Error en busqueda: {str(e)}")
            return []
    
    def search_lessons_advanced(self, query, category=None, difficulty=None):
        """Busqueda avanzada de lecciones con filtros"""
        results = self.search_lessons(query)
        if category:
            results = [r for r in results if r.get('categoria', '').lower() == category.lower()]
        if difficulty is not None:
            results = [r for r in results if r.get('dificultad') == difficulty]
        return results
    
    # ============================================
    # OPERACIONES DE PROGRESO DEL USUARIO
    # ============================================
    
    def update_user_progress(self, user_id, lesson_id, completed=True):
        """Actualizar el progreso de un usuario"""
        if self.offline_mode:
            user = self.mock_db['users'].get(user_id)
            if not user:
                return False, "Usuario no encontrado"
            progress = user.get('progress', {})
            completed_lessons = progress.get('completed_lessons', [])
            if completed and lesson_id not in completed_lessons:
                completed_lessons.append(lesson_id)
                progress['completed_lessons'] = completed_lessons
                progress['total_points'] = progress.get('total_points', 0) + 10
                user['progress'] = progress
                return True, "Progreso actualizado (offline)"
            return True, "Sin cambios"
        
        try:
            user_ref = self.db.collection(Config.USERS_COLLECTION).document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                return False, "Usuario no encontrado"
            
            user_data = user_doc.to_dict()
            progress = user_data.get('progress', {})
            completed_lessons = progress.get('completed_lessons', [])
            
            if completed and lesson_id not in completed_lessons:
                completed_lessons.append(lesson_id)
                progress['completed_lessons'] = completed_lessons
                progress['total_points'] = progress.get('total_points', 0) + 10
                
                user_ref.update({'progress': progress})
                return True, "Progreso actualizado"
            
            return True, "Sin cambios"
            
        except Exception as e:
            return False, f"Error al actualizar progreso: {str(e)}"
    
    def get_user_progress(self, user_id):
        """Obtener el progreso de un usuario"""
        if self.offline_mode:
            user = self.mock_db['users'].get(user_id)
            if user:
                return user.get('progress', {})
            return {}
        
        try:
            user = self.db.collection(Config.USERS_COLLECTION).document(user_id).get()
            if user.exists:
                return user.to_dict().get('progress', {})
            return {}
        except Exception as e:
            print(f"Error al obtener progreso: {str(e)}")
            return {}
    
    def save_placement_test_results(self, user_id, scores, unlocked_categories):
        """Guardar resultados del placement test"""
        if self.offline_mode:
            user = self.mock_db['users'].get(user_id)
            if not user:
                return False, "Usuario no encontrado"
            progress = user.get('progress', {})
            progress['placement_test'] = {'scores': scores}
            progress['unlocked_categories'] = unlocked_categories
            progress['placement_test_completed'] = True
            user['progress'] = progress
            return True, "Resultados guardados (offline)"
        
        try:
            user_ref = self.db.collection(Config.USERS_COLLECTION).document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                return False, "Usuario no encontrado"
            
            user_data = user_doc.to_dict()
            progress = user_data.get('progress', {})
            
            progress['placement_test'] = {
                'scores': scores,
                'completed_at': firestore.SERVER_TIMESTAMP
            }
            progress['unlocked_categories'] = unlocked_categories
            progress['placement_test_completed'] = True
            
            user_ref.update({'progress': progress})
            return True, "Resultados guardados"
            
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def unlock_all_lessons_for_category(self, user_id, category):
        """Marcar todas las lecciones de una categoria como completadas"""
        if self.offline_mode:
            user = self.mock_db['users'].get(user_id)
            if not user:
                return False, 0
            lessons = self.get_lessons_by_category(category)
            progress = user.get('progress', {})
            completed_lessons = progress.get('completed_lessons', [])
            count = 0
            for lesson in lessons:
                lid = lesson.get('id')
                if lid and lid not in completed_lessons:
                    completed_lessons.append(lid)
                    count += 1
            progress['completed_lessons'] = completed_lessons
            progress['total_points'] = progress.get('total_points', 0) + (count * 10)
            user['progress'] = progress
            return True, count
        
        try:
            lessons = self.get_lessons_by_category(category)
            
            user_ref = self.db.collection(Config.USERS_COLLECTION).document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                return False, 0
            
            user_data = user_doc.to_dict()
            progress = user_data.get('progress', {})
            completed_lessons = progress.get('completed_lessons', [])
            
            count = 0
            for lesson in lessons:
                lesson_id = lesson.get('id')
                if lesson_id and lesson_id not in completed_lessons:
                    completed_lessons.append(lesson_id)
                    count += 1
            
            progress['completed_lessons'] = completed_lessons
            progress['total_points'] = progress.get('total_points', 0) + (count * 10)
            
            user_ref.update({'progress': progress})
            return True, count
            
        except Exception as e:
            print(f"Error: {str(e)}")
            return False, 0


# Crear instancia global
firebase_service = FirebaseService()
