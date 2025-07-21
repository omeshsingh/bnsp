# list_models.py
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables to get the API key
load_dotenv()

# Configure the API with your key
try:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in .env file.")
    
    genai.configure(api_key=api_key)
    
    print("--- Available Google AI Models ---")
    
    # List all models
    for m in genai.list_models():
        # We are interested in models that support the 'generateContent' method, which is used for chat/text generation.
        if 'generateContent' in m.supported_generation_methods:
            print(f"Model Name: {m.name}")
            print(f"  - Supported Methods: {m.supported_generation_methods}")
            print(f"  - Display Name: {m.display_name}")
            print("-" * 20)

except Exception as e:
    print(f"An error occurred: {e}")