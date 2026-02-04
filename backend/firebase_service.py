"""
Servicio de conexión y operaciones con Firebase
"""
import firebase_admin
from firebase_admin import credentials, firestore, auth
from config import Config
import os


class FirebaseService:
    """Servicio singleton para manejar la conexión con Firebase"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Patrón Singleton - solo una instancia de Firebase"""
        if cls._instance is None:
            cls._instance = super(FirebaseService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializar la conexión con Firebase"""
        if not FirebaseService._initialized:
            self._initialize_firebase()
            FirebaseService._initialized = True
    
    def _initialize_firebase(self):
        """Inicializar Firebase Admin SDK"""
        try:
            # Verificar que el archivo de credenciales existe
            if not os.path.exists(Config.FIREBASE_CREDENTIALS):
                raise FileNotFoundError(
                    f"⚠️  No se encontró el archivo de credenciales: {Config.FIREBASE_CREDENTIALS}\n"
                    f"Por favor, sigue la GUIA_CONFIGURACION_FIREBASE.md"
                )
            
            # Inicializar Firebase con las credenciales
            cred = credentials.Certificate(Config.FIREBASE_CREDENTIALS)
            firebase_admin.initialize_app(cred)
            
            # Obtener referencia a Firestore
            self.db = firestore.client()
            
            print("✅ Firebase inicializado correctamente")
            
        except Exception as e:
            print(f"❌ Error al inicializar Firebase: {str(e)}")
            raise
    
    # ============================================
    # OPERACIONES DE AUTENTICACIÓN
    # ============================================
    
    def create_user(self, email, password, username):
        """
        Crear un nuevo usuario en Firebase Authentication y Firestore
        
        Args:
            email (str): Email del usuario
            password (str): Contraseña
            username (str): Nombre de usuario
            
        Returns:
            tuple: (success, message, user_id)
        """
        try:
            # Crear usuario en Firebase Authentication
            user = auth.create_user(
                email=email,
                password=password,
                display_name=username
            )
            
            # Guardar información adicional en Firestore
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
            return False, "El email ya está registrado", None
        except Exception as e:
            return False, f"Error al crear usuario: {str(e)}", None
    
    def verify_user(self, email, password):
        """
        Verificar credenciales de usuario
        
        Nota: Firebase Admin SDK no permite verificar contraseñas directamente.
        En producción, esto se hace desde el cliente con Firebase Auth SDK.
        Esta función es un placeholder para mantener compatibilidad con tu código.
        
        Args:
            email (str): Email del usuario
            password (str): Contraseña
            
        Returns:
            tuple: (success, message, user_data)
        """
        try:
            # Obtener usuario por email
            user = auth.get_user_by_email(email)
            
            # En una app real, la verificación de contraseña se hace en el cliente
            # Aquí retornamos los datos del usuario si existe
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
        """
        Buscar usuario por nombre de usuario
        
        Args:
            username (str): Nombre de usuario
            
        Returns:
            dict or None: Datos del usuario o None si no existe
        """
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
        """
        Verificar si un usuario o email ya existe
        
        Args:
            username (str, optional): Nombre de usuario
            email (str, optional): Email
            
        Returns:
            bool: True si existe, False si no
        """
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
        """
        Agregar una lección a Firestore
        
        Args:
            lesson_data (dict): Datos de la lección
            
        Returns:
            tuple: (success, message, lesson_id)
        """
        try:
            doc_ref = self.db.collection(Config.LESSONS_COLLECTION).add(lesson_data)
            return True, "Lección agregada exitosamente", doc_ref[1].id
        except Exception as e:
            return False, f"Error al agregar lección: {str(e)}", None
    
    def get_lessons_by_category(self, category):
        """
        Obtener lecciones por categoría
        
        Args:
            category (str): Categoría (Python Básico, Intermedio, Avanzado)
            
        Returns:
            list: Lista de lecciones
        """
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
        """
        Obtener todas las lecciones
        
        Returns:
            list: Lista de todas las lecciones
        """
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
        """
        Obtener una lección específica
        
        Args:
            lesson_id (str): ID de la lección
            
        Returns:
            dict or None: Datos de la lección
        """
        try:
            lesson = self.db.collection(Config.LESSONS_COLLECTION).document(lesson_id).get()
            if lesson.exists:
                return {**lesson.to_dict(), 'id': lesson.id}
            return None
        except Exception as e:
            print(f"Error al obtener lección: {str(e)}")
            return None
    
    # ============================================
    # OPERACIONES DE PROGRESO DEL USUARIO
    # ============================================
    
    def update_user_progress(self, user_id, lesson_id, completed=True):
        """
        Actualizar el progreso de un usuario
        
        Args:
            user_id (str): ID del usuario
            lesson_id (str): ID de la lección
            completed (bool): Si completó la lección
            
        Returns:
            tuple: (success, message)
        """
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
        """
        Obtener el progreso de un usuario
        
        Args:
            user_id (str): ID del usuario
            
        Returns:
            dict: Progreso del usuario
        """
        try:
            user = self.db.collection(Config.USERS_COLLECTION).document(user_id).get()
            if user.exists:
                return user.to_dict().get('progress', {})
            return {}
        except Exception as e:
            print(f"Error al obtener progreso: {str(e)}")
            return {}


# Crear instancia global
firebase_service = FirebaseService()