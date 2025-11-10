from adk.server import app
from adk.sessions import FirestoreSessionService
from app.agent import get_agent
import uvicorn
import os
from google.cloud import firestore

def test_firestore_connection():
    """
    Performs a simple read operation to test the Firestore connection and permissions.
    This runs before the server starts to provide a clear startup signal.
    """
    print("Attempting to test Firestore connection...")
    try:
        # In a GCP environment, the client automatically finds the project ID.
        db = firestore.Client()
        doc_ref = db.collection("firestore-connection-test").document("startup-test-doc")
        doc_ref.get()
        print("Firestore connection test successful.")
    except Exception as e:
        print("!!! CRITICAL: Firestore connection test FAILED. !!!")
        print(f"Error: {e}")
        print("This is likely an IAM permissions issue. Ensure the service account has the 'Cloud Datastore User' role.")
        # In a real scenario, you might want to exit here if Firestore is critical
        # raise e 

# Run the diagnostic test on startup, before the app starts
test_firestore_connection()

# Create an instance of the Firestore session service.
session_service = FirestoreSessionService()

# Get the main agent application instance
agent_app = app.create_app(
    agent=get_agent(),
    session_service=session_service
)

if __name__ == "__main__":
    # Respect the PORT environment variable provided by Cloud Run.
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(agent_app, host="0.0.0.0", port=port)
