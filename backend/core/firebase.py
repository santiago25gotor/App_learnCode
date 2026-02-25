import firebase_admin
from firebase_admin import credentials, firestore, auth
from config import Config
import os
import cloudinary
import cloudinary.uploader

class FirebaseService:

    _instance = None
    _initialized = False
    
    cloudinary.config(
        cloud_name=Config.CLOUDINARY_CLOUD_NAME,
        api_key=Config.CLOUDINARY_API_KEY,
        api_secret=Config.CLOUDINARY_API_SECRET,
        secure=True
    )

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not FirebaseService._initialized:
            self._initialize_firebase()
            FirebaseService._initialized = True
    
    def _initialize_firebase(self):
        self.db = None
        self._connect_firebase()

    def _connect_firebase(self):
        cred_path = Config.FIREBASE_CREDENTIALS
        
        if not os.path.exists(cred_path):
            raise FileNotFoundError(f"No se encontró el archivo de credenciales: {cred_path}")

        if not len(firebase_admin._apps):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        
        self.db = firestore.client()
        print("[OK] Firebase conectado correctamente")

    def create_user(self, email, password, username):
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
        try:
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={Config.FIREBASE_WEB_API_KEY}"
            
            payload = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }

            import requests
            response = requests.post(url, json=payload)
            data = response.json()

            if response.status_code != 200:
                return False, "Email o contraseña incorrectos", None

            uid = data.get("localId")

            user_doc = self.db.collection(Config.USERS_COLLECTION).document(uid).get()

            if user_doc.exists:
                user_data = user_doc.to_dict()
                user_data['uid'] = uid
                return True, "Login exitoso", user_data
            else:
                return False, "Usuario no encontrado en la base de datos", None

        except Exception as e:
            return False, f"Error al verificar usuario: {str(e)}", None
    
    def get_user_by_username(self, username):
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
    
    def add_lesson(self, lesson_data):
        try:
            doc_ref = self.db.collection(Config.LESSONS_COLLECTION).add(lesson_data)
            return True, "Leccion agregada exitosamente", doc_ref[1].id
        except Exception as e:
            return False, f"Error al agregar leccion: {str(e)}", None
    
    def get_lessons_by_category(self, category):
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
        try:
            lesson = self.db.collection(Config.LESSONS_COLLECTION).document(lesson_id).get()
            if lesson.exists:
                return {**lesson.to_dict(), 'id': lesson.id}
            return None
        except Exception as e:
            print(f"Error al obtener leccion: {str(e)}")
            return None
        
    def search_lessons(self, query):
        try:
            query = query.lower().strip()
            if not query:
                return []
            
            query_words = query.split()
            query_nospace = query.replace(' ', '')

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
                searchable_nospace = searchable_text.replace(' ', '')

                if (query in searchable_text or
                    query_nospace in searchable_nospace or
                    any(word in searchable_text for word in query_words)):
                    results.append({**data, "id": lesson.id})

            results.sort(key=lambda x: (
                not all(word in str(x.get("titulo", "")).lower() for word in query_words),
                not any(word in str(x.get("titulo", "")).lower() for word in query_words),
                x.get("numero_leccion", 0)
            ))

            return results

        except Exception as e:
            print(f"[ERROR] Error en búsqueda: {str(e)}")
            return []
        
    def search_lessons_advanced(self, query, category=None, difficulty=None):
        results = self.search_lessons(query)
        if category:
            results = [r for r in results if r.get('categoria', '').lower() == category.lower()]
        if difficulty is not None:
            results = [r for r in results if r.get('dificultad') == difficulty]
        return results

    def update_user_progress(self, user_id, lesson_id, completed=True):
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
        try:
            user = self.db.collection(Config.USERS_COLLECTION).document(user_id).get()
            if user.exists:
                return user.to_dict().get('progress', {})
            return {}
        except Exception as e:
            print(f"Error al obtener progreso: {str(e)}")
            return {}
    
    def save_placement_test_results(self, user_id, scores, unlocked_categories):
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
    
    def mass_unlock_lessons(self, user_id, category=None):
        try:
            if category:
                lessons = self.get_lessons_by_category(category)
            else:
                lessons = self.get_all_lessons()

            if not lessons:
                return False, "No se encontraron lecciones para desbloquear"

            user_ref = self.db.collection(Config.USERS_COLLECTION).document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                return False, "Usuario no encontrado"

            user_data = user_doc.to_dict()
            progress = user_data.get('progress', {
                'completed_lessons': [],
                'total_points': 0,
                'unlocked_categories': ['Python Básico']
            })

            current_completed = set(progress.get('completed_lessons', []))
            new_lessons = [l.get('id') for l in lessons if l.get('id') not in current_completed]
            
            if not new_lessons:
                return True, 0

            progress['completed_lessons'] = list(current_completed.union(new_lessons))
            progress['total_points'] = progress.get('total_points', 0) + (len(new_lessons) * 10)
            
            if not category:
                progress['unlocked_categories'] = Config.LESSON_CATEGORIES

            batch = self.db.batch()
            batch.update(user_ref, {'progress': progress})
            batch.commit()

            return True, len(new_lessons)

        except Exception as e:
            print(f"Error en mass_unlock: {str(e)}")
            return False, str(e)
        
    def upload_user_avatar_cloudinary(self, user_id, file_stream):

        try:
            result = cloudinary.uploader.upload(
                file_stream,
                folder=f"avatars/{user_id}",
                public_id="profile",
                overwrite=True,
                resource_type="image"
            )

            avatar_url = result.get("secure_url")

            # Guardar URL en Firestore
            self.db.collection(Config.USERS_COLLECTION).document(user_id).update({
                "avatar": avatar_url
            })

            return True, avatar_url

        except Exception as e:
            return False, str(e)
            

firebase_service = FirebaseService()