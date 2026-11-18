import firebase_admin
from firebase_admin import credentials
from app.core.config import settings

def initialize_firebase() -> firebase_admin.App:
    """
    Initialize Firebase Admin SDK once.

    Returns:
        Firebase Admin application instance.
    """
    
    try:
        firebase_admin.get_app()
        
    except ValueError:
        firebase_credentials = credentials.Certificate(settings.firebase_credentials_path)
        firebase_app = firebase_admin.initialize_app(firebase_credentials)
        return firebase_app
    