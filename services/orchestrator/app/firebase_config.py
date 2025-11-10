import firebase_admin
from firebase_admin import credentials, firestore, auth
from google.cloud import firestore as google_firestore
import json

# --- Global Firebase/Firestore Instances ---
# We initialize them as None and then set them up
# in the main initialization function.

db = None
app = None
auth_client = None

def initialize_firebase():
    """
    Initializes the Firebase Admin SDK.
    It uses the __firebase_config and __initial_auth_token global variables
    provided by the ADK environment.
    """
    global db, app, auth_client

    # Only initialize if it hasn't been done already
    if app:
        return

    try:
        # These globals are expected to be injected by the environment.
        if '__firebase_config' not in globals():
            print("Warning: __firebase_config is not defined. Using default settings.")
            # Fallback for local testing if needed, though this will likely fail
            # without real credentials.
            cred = credentials.ApplicationDefault()
        else:
            # Parse the config string provided by the environment
            firebase_config = json.loads(__firebase_config)
            cred = credentials.Certificate(firebase_config)
        
        print("Initializing Firebase App...")
        app = firebase_admin.initialize_app(cred)
        
        # Use google_firestore.Client() for the modern Python library
        # which works well with `google-cloud-firestore`
        db = google_firestore.Client()
        
        # Initialize Firebase Auth client
        auth_client = auth.Client(app)
        
        print("Firebase App and Firestore Client initialized successfully.")

        # --- Handle Authentication ---
        # The environment provides an __initial_auth_token
        # We need to sign in with it to get a user session.
        if '__initial_auth_token' in globals() and __initial_auth_token:
            try:
                # This step isn't strictly necessary for the *Admin* SDK
                # (which has full privileges), but it's good practice
                # to verify the token if we need to get a user_id.
                # For Admin SDK, we can often just get the user_id from
                # the frontend and trust it (after it passes security rules).
                
                # A better pattern for the backend is to get the user's ID
                # token from the frontend request, verify it, and get the uid.
                # For this ADK setup, we'll assume the frontend will pass the
                # user_id (auth.currentUser.uid) with its requests.
                print("Firebase auth token provided.")
                # We don't need to sign in on the *backend* with the admin SDK.
                # We just need to be ready to *verify* tokens from the frontend
                # or use the `db` object with admin rights.
                
            except Exception as e:
                print(f"Warning: Could not verify initial auth token: {e}")
        else:
            print("No initial auth token provided. Running in anonymous/admin mode.")

    except Exception as e:
        print(f"CRITICAL: Failed to initialize Firebase: {e}")
        # If this fails, the app can't work.
        db = None
        auth_client = None

# Call initialization when this module is imported
initialize_firebase()