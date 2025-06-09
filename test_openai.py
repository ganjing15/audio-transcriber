import os
from dotenv import load_dotenv
from openai import OpenAI
import json

# Load environment variables
print("Loading environment variables...")
load_dotenv()

# Get and validate API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("ERROR: No API key found in environment variables.")
    print("Please check your .env file and ensure OPENAI_API_KEY is set.")
    exit(1)

print(f"API Key found (first 5 chars): {api_key[:5]}...")

# Try to initialize OpenAI client
try:
    print("Initializing OpenAI client...")
    client = OpenAI(api_key=api_key)
    print("Client initialized successfully.")
except Exception as e:
    print(f"ERROR initializing OpenAI client: {e}")
    exit(1)

# Try a simple API call (models list)
try:
    print("\nTesting API connection with models.list()...")
    models = client.models.list()
    print("API connection successful! Available models:")
    for model in models.data[:5]:  # Show first 5 models
        print(f" - {model.id}")
    print("... and more")
except Exception as e:
    print(f"ERROR connecting to OpenAI API: {e}")
    import traceback
    print(traceback.format_exc())
    exit(1)

print("\nAPI validation successful! Your OpenAI API key works correctly.")
