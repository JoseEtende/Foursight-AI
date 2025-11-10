import firebase_admin
from firebase_admin import credentials
from google.cloud import firestore
import os

db = None

def initialize_firebase():
    """
    Initializes the Firebase Admin SDK using environment variables.
    """
    global db
    if db:
        return

    try:
        # Use GOOGLE_APPLICATION_CREDENTIALS for production on Cloud Run
        if 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ:
            cred = credentials.ApplicationDefault()
        else:
            # Fallback for local development - requires manual setup of credentials file
            # Ensure you have run 'gcloud auth application-default login'
            print("Warning: GOOGLE_APPLICATION_CREDENTIALS not set. Using Application Default Credentials for local dev.")
            cred = credentials.ApplicationDefault()

        firebase_admin.initialize_app(cred)
        db = firestore.Client()
        print("Firebase App and Firestore Client initialized successfully.")

    except Exception as e:
        print(f"CRITICAL: Failed to initialize Firebase: {e}")
        db = None

initialize_firebase()
