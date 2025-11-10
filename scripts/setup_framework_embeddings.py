import os
import json
import asyncio
from google.cloud import firestore
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
# Ensure the GEMINI_API_KEY environment variable is set for embedding generation
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", os.environ.get("GOOGLE_API_KEY"))
if not GEMINI_API_KEY:
    print("FATAL: GEMINI_API_KEY or GOOGLE_API_KEY environment variable is not set.")
    exit(1)

# Configure the generative AI client
genai.configure(api_key=GEMINI_API_KEY)

# Path to the framework descriptions relative to the script execution directory
DESCRIPTIONS_PATH = 'scripts/framework_descriptions'

def delete_all_frameworks(db: firestore.Client):
    """Deletes all documents in the 'frameworks' collection."""
    print("--- STARTING CLEANUP ---")
    frameworks_collection = db.collection('frameworks')
    
    # Batch delete operation (Firestore limitation: max 500 in one batch)
    deleted_count = 0
    while True:
        docs = frameworks_collection.limit(500).stream()
        deleted_batch_count = 0
        batch = db.batch()
        
        for doc in docs:
            batch.delete(doc.reference)
            deleted_batch_count += 1
            deleted_count += 1
            
        if deleted_batch_count == 0:
            break
            
        batch.commit()
        print(f"  > Deleted {deleted_batch_count} documents in a batch.")

    print(f"Cleanup complete. Total documents deleted: {deleted_count}")
    print("--- CLEANUP ENDED ---")


def setup_embeddings():
    """
    Initializes Firestore, deletes old data, reads framework definitions,
    generates embeddings, and writes new data back to Firestore.
    """
    try:
        # Initialize Firestore client (relies on Application Default Credentials for local execution)
        db = firestore.Client()
        print("Firestore client initialized successfully.")
    except Exception as e:
        print(f"Error initializing Firestore client: {e}")
        print("Ensure you are authenticated with 'gcloud auth application-default login'.")
        return

    # 1. Clean up existing data
    delete_all_frameworks(db)

    # 2. Process and add new embeddings
    frameworks_collection = db.collection('frameworks')

    print("\n--- STARTING EMBEDDING GENERATION AND UPLOAD ---")
    
    # Check if the descriptions path exists
    if not os.path.isdir(DESCRIPTIONS_PATH):
        print(f"FATAL: Descriptions path '{DESCRIPTIONS_PATH}' not found.")
        print("Please ensure this script is run from the root directory of the project.")
        return

    # Iterate over the markdown files in the directory
    for filename in os.listdir(DESCRIPTIONS_PATH):
        if filename.endswith('.md'):
            filepath = os.path.join(DESCRIPTIONS_PATH, filename)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                description = f.read()
            
            # Extract framework name from filename (e.g., 'swot_analysis.md' -> 'swot_analysis')
            framework_name = filename.replace('.md', '')

            print(f"Processing: {framework_name}...")
            
            try:
                # Generate vector embedding for the description
                # Using a highly-optimized model for embedding retrieval
                result = genai.embed_content(
                    model="models/embedding-001",
                    content=description,
                    task_type="RETRIEVAL_DOCUMENT"
                )
                embedding = result['embedding']
    
                # Create a new document in the 'frameworks' collection
                framework_doc = {
                    'name': framework_name,
                    'description': description,
                    'embedding': embedding
                }
                
                # Use framework name as the document ID
                frameworks_collection.document(framework_name).set(framework_doc)
                print(f'  > SUCCESS: Added {framework_name} to Firestore.')

            except Exception as e:
                print(f'  > ERROR: Failed to generate embedding or upload for {framework_name}. Error: {e}')
                continue

    print("--- UPLOAD COMPLETE ---")

if __name__ == '__main__':
    # This script is intended to be run locally, not inside the ADK server process
    # To run: `python setup_framework_embeddings.py` (ensure dependencies are installed)
    setup_embeddings()