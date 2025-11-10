from adk.server import app
from adk.sessions import FirestoreSessionService
from app.agent import get_agent
import uvicorn
import os
from google.cloud import firestore

def test_firestore_connection():
    """
    Performs a simple read operation to test the Firestore connection and permissions.
    """
    print("Attempting to test Firestore connection...")
    try:
        project_id = os.environ.get("GCP_PROJECT_ID")
        if not project_id:
            print("GCP_PROJECT_ID environment variable not set. Cannot test Firestore connection.")
            return

        db = firestore.Client(project=project_id)
        # Attempt to get a document that likely doesn't exist.
        # We just want to see if the request authenticates and is authorized.
        doc_ref = db.collection("firestore-connection-test").document("test-doc")
        doc = doc_ref.get()
        print("Firestore connection test successful. Document exists:", doc.exists)
    except Exception as e:
        print("!!! CRITICAL: Firestore connection test FAILED. !!!")
        print(f"Error: {e}")
        print("This is likely an IAM permissions issue. Ensure the service account for this Cloud Run service has the 'Cloud Datastore User' or 'Firebase User' role.")

# Create an instance of the Firestore session service.
session_service = FirestoreSessionService()

# Get the main agent application instance
agent_app = app.create_app(
    agent=get_agent(),
    session_service=session_service
)

if __name__ == "__main__":
    # Run the diagnostic test on startup
    test_firestore_connection()
    
    # Run the server with uvicorn.
    uvicorn.run(agent_app, host="0.0.0.0", port=8080)
