# create_vectordb_gemini.py
import pandas as pd
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document # Updated import
import os
from dotenv import load_dotenv

load_dotenv()

# Check for Google API Key
if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("GOOGLE_API_KEY not found in .env file. Please get it from Google AI Studio.")

CSV_FILE_PATH = "cleaned_bns.csv"
DB_DIRECTORY = "chroma_db_gemini" # Use a new directory to avoid conflicts

def create_vector_database():
    print(f"Reading data from {CSV_FILE_PATH}...")
    df = pd.read_csv(CSV_FILE_PATH)
    
    documents = [
        Document(
            page_content=f"Section {row.bns_section_number}: {row.bns_section_title}. Details: {row.bns_section_text}",
            metadata={
                "bns_section_number": str(row.bns_section_number),
                "bns_section_title": str(row.bns_section_title),
                "crime_category": str(row.crime_category),
            }
        )
        for row in df.itertuples()
    ]
    print(f"Created {len(documents)} documents to be embedded.")
    
    print("Initializing Google Gemini embeddings model...")
    # Use the recommended model for embeddings
    embedding_function = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    print(f"Creating and persisting vector database in '{DB_DIRECTORY}'...")
    db = Chroma.from_documents(
        documents=documents, 
        embedding=embedding_function,
        persist_directory=DB_DIRECTORY
    )
    
    print("\nSUCCESS: Gemini-powered vector database created successfully.")

if __name__ == "__main__":
    create_vector_database()