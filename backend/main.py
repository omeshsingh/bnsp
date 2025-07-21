# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware # Import CORS
from pydantic import BaseModel
from typing import List, Optional
import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv

# --- LangChain and Google Gemini Imports (Updated for v0.1+) ---
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableMap
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

# Load environment variables (for GOOGLE_API_KEY)
load_dotenv()
if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("GOOGLE_API_KEY not found in .env file. Please get it from Google AI Studio.")

# --- Initialize Firebase Admin SDK ---
CREDENTIALS_FILE = "firebase-credentials.json"
# ... (keep the rest of your Firebase init code) ...
cred = credentials.Certificate(CREDENTIALS_FILE)
firebase_admin.initialize_app(cred)
db = firestore.client()
COLLECTION_NAME = "crime_sections"

# --- Load the Gemini Vector Database ---
print("Loading Gemini Vector DB from disk...")
embedding_function = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
vector_db = Chroma(persist_directory="chroma_db_gemini", embedding_function=embedding_function)
retriever = vector_db.as_retriever(search_kwargs={"k": 5}) # Retrieve top 5 results
print("Gemini Vector DB loaded successfully.")

# --- FastAPI App and Pydantic Models ---
app = FastAPI(title="Police Assist BNS API (Gemini)")

# --- Add CORS Middleware ---
origins = [
    "http://localhost:3000", # The origin of your React frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (GET, POST, etc.)
    allow_headers=["*"], # Allows all headers
)


class SectionRequest(BaseModel):
    keywords: List[str]

class SectionResponse(BaseModel):
    bns_section_number: str
    bns_section_title: str
    bns_section_text: str
    keywords: List[str]
    crime_category: str
    match_count: int

class DescriptionRequest(BaseModel):
    description: str

class AiResponse(BaseModel):
    analysis: str
    suggested_sections: List[dict]

# --- Keyword Search Endpoint (No changes needed) ---
@app.post("/suggest-sections", response_model=List[SectionResponse])
async def suggest_sections(request: SectionRequest):
    # ... (This function remains exactly the same as the working version) ...
    if not request.keywords: return []
    try:
        user_keywords = {k.strip().lower() for k in request.keywords}
        collection_ref = db.collection(COLLECTION_NAME)
        docs = collection_ref.stream()
        results_with_scores = []
        for doc in docs:
            data = doc.to_dict()
            section_keywords = {k.lower() for k in data.get('keywords', [])}
            if user_keywords.intersection(section_keywords):
                match_count = len(user_keywords.intersection(section_keywords))
                data['match_count'] = match_count
                results_with_scores.append(data)
        sorted_results = sorted(results_with_scores, key=lambda x: x['match_count'], reverse=True)
        return sorted_results
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while querying the database.")

# --- NEW GEMINI-POWERED AI ENDPOINT ---
@app.post("/analyse-description", response_model=AiResponse)
async def analyse_description(request: DescriptionRequest):
    """
    Takes a detailed crime description, finds relevant BNS sections using Gemini embeddings,
    and uses the Gemini Pro model to generate a reasoned analysis.
    """
    print(f"Received description for Gemini analysis: {request.description}")

    template = """
    You are an expert legal assistant for Indian Police Officers.
    Your task is to analyze a crime description and suggest the most appropriate BNS sections based ONLY on the provided legal texts.
    Provide a step-by-step reasoning for each section you suggest.
    
    CRIME DESCRIPTION:
    {description}
    
    RELEVANT LEGAL TEXTS:
    {context}
    
    ANALYSIS:
    """
    prompt = ChatPromptTemplate.from_template(template)

    # Use the Gemini Pro model
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)

    # The LangChain "chain" remains structurally the same
    chain = (
        {"context": retriever, "description": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    try:
        analysis_text = chain.invoke(request.description)
        
        retrieved_docs = retriever.invoke(request.description)
        suggested_sections = [doc.metadata for doc in retrieved_docs]

        return AiResponse(analysis=analysis_text, suggested_sections=suggested_sections)

    except Exception as e:
        print(f"Error during Gemini AI analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    # In main.py

# A response model without the match_count
class SectionDetailResponse(BaseModel):
    bns_section_number: str
    bns_section_title: str
    bns_section_text: str
    keywords: List[str]
    crime_category: str


# --- NEW "SECTION DETAIL" ENDPOINT ---
@app.get("/sections/{section_number}", response_model=SectionDetailResponse)
async def get_section_details(section_number: str):
    """
    Retrieves all details for a single, specific BNS section by its number.
    The section number can contain characters like '64(1)', so it's a string.
    """
    print(f"Fetching details for section: {section_number}")
    try:
        # Get a reference to the specific document in the collection
        doc_ref = db.collection(COLLECTION_NAME).document(section_number)
        
        # Retrieve the document
        doc = doc_ref.get()
        
        # Check if the document exists
        if doc.exists:
            # Return the document's data, which will be validated by the Pydantic model
            return doc.to_dict()
        else:
            # If no document is found with that ID, raise a 404 error
            raise HTTPException(status_code=404, detail=f"Section '{section_number}' not found.")
            
    except Exception as e:
        print(f"Error fetching section details for '{section_number}': {e}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching data from the database.")

class IPCtoBNSRequest(BaseModel):
    ipc_section: str
    description: Optional[str] = None

class IPCtoBNSResponse(BaseModel):
    analysis: str
    suggested_sections: List[dict]

@app.post("/convert-ipc-to-bns", response_model=IPCtoBNSResponse)
async def convert_ipc_to_bns(request: IPCtoBNSRequest):
    """
    Given an IPC section (and optional description), suggest the most relevant BNS section(s) and provide reasoning.
    """
    print(f"Received IPC section for conversion: {request.ipc_section}, description: {request.description}")

    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
    
    # Step 1: Determine the search query. Use user's description if available, otherwise ask AI.
    search_query = request.description
    if not search_query:
        print(f"No description for IPC {request.ipc_section}. Using AI to generate one for search.")
        get_desc_prompt = ChatPromptTemplate.from_template(
            "What is the crime associated with Indian Penal Code (IPC) Section {ipc_section}? Provide a short, concise description (e.g., 'Punishment for murder')."
        )
        desc_chain = get_desc_prompt | llm | StrOutputParser()
        search_query = desc_chain.invoke({"ipc_section": request.ipc_section})
        print(f"AI-generated search query: '{search_query}'")

    # Step 2: Define the main prompt for the final analysis.
    template = """
    You are an expert legal assistant for Indian Police Officers.
    Your task is to map an IPC (Indian Penal Code) section to the most relevant BNS (Bharatiya Nyaya Sanhita) section(s).
    Use the provided IPC section number and its description to find the best-matching BNS section(s) from the legal texts provided as context.
    Provide a step-by-step reasoning for your mapping.

    IPC SECTION: {ipc_section}
    DESCRIPTION: {description}

    RELEVANT BNS LEGAL TEXTS (CONTEXT):
    {context}

    ANALYSIS:
    """
    prompt = ChatPromptTemplate.from_template(template)

    # Step 3: Define the main chain to perform the analysis.
    chain = (
        {
            "context": lambda x: retriever.invoke(x["description"]), # Use the (potentially AI-generated) description for retrieval
            "ipc_section": RunnablePassthrough(),
            "description": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    try:
        # Step 4: Invoke the chain with the IPC section and the determined search query.
        analysis_text = chain.invoke({
            "ipc_section": request.ipc_section,
            "description": search_query
        })
        
        # Use the same search query to retrieve the final list of suggested sections.
        retrieved_docs = retriever.invoke(search_query)
        suggested_sections = [doc.metadata for doc in retrieved_docs]

        return IPCtoBNSResponse(analysis=analysis_text, suggested_sections=suggested_sections)
    except Exception as e:
        print(f"Error during IPC-to-BNS conversion: {e}")
        raise HTTPException(status_code=500, detail=str(e))