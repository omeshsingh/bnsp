# firebase_importer.py
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import os

# --- 1. Initialize Firebase Admin SDK ---
# It's good practice to get the path from an environment variable
# but for simplicity, we'll hardcode it. Ensure the file is in the same directory.
CREDENTIALS_FILE = "firebase-credentials.json"
if not os.path.exists(CREDENTIALS_FILE):
    raise FileNotFoundError(f"'{CREDENTIALS_FILE}' not found. Please download it from your Firebase project settings.")

cred = credentials.Certificate(CREDENTIALS_FILE)
firebase_admin.initialize_app(cred)

db = firestore.client()

CSV_FILE_PATH = "cleaned_bns.csv"
COLLECTION_NAME = "crime_sections"

def import_data():
    try:
        print("--- Using PANDAS to import data to Firebase Firestore ---")
        
        collection_ref = db.collection(COLLECTION_NAME)
        
        docs = collection_ref.limit(1).stream()
        if len(list(docs)) > 0:
            print(f"The '{COLLECTION_NAME}' collection already has data. To re-import, please delete the collection in the Firebase console first.")
            return

        print(f"Collection is empty. Reading data from {CSV_FILE_PATH}...")
        df = pd.read_csv(CSV_FILE_PATH)
        
        batch = db.batch()
        count = 0
        for row in df.itertuples(index=False):
            print(f"Processing Section: {row.bns_section_number}")
            
            # Sanitize and split keywords into a proper list
            keywords_list = [k.strip() for k in str(row.keywords).split(',')]
            
            # Create a dictionary for the new document
            data = {
                'bns_section_number': str(row.bns_section_number),
                'bns_section_title': row.bns_section_title,
                'bns_section_text': row.bns_section_text,
                'keywords': keywords_list,
                'crime_category': row.crime_category
            }
            
            # Use the BNS section number as the unique ID for the document
            doc_ref = collection_ref.document(str(row.bns_section_number))
            batch.set(doc_ref, data)
            
            count += 1
            # Commit the batch every 499 documents to stay within limits
            if count % 499 == 0:
                print(f"Committing batch of {count} documents...")
                batch.commit()
                batch = db.batch() # Start a new batch

        # Commit any remaining documents in the last batch
        if count > 0:
            batch.commit()
        
        print(f"\nSUCCESS: Successfully imported {count} sections to Firestore.")

    except FileNotFoundError:
        print(f"ERROR: The file {CSV_FILE_PATH} was not found.")
    except Exception as e:
        print(f"\nAN ERROR OCCURRED: {e}")

if __name__ == "__main__":
    import_data()