import sys
sys.path.insert(0, '.')
from backend.core.firebase import firebase_service
from config import Config

db = firebase_service.db
ref = db.collection(Config.USERS_COLLECTION).document("WT6VnOur0GVuSPTCBQOUgh79p1t1")
ref.update({'role': 'superadmin'})
print("Listo! Ya eres SuperAdmin")