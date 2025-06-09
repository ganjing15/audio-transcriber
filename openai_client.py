import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("WARNING: OPENAI_API_KEY is not set in the environment variables")
    print("Please make sure you have a .env file with a valid API key")

print(f"API Key available: {bool(api_key)}")
if api_key:
    print(f"API Key starts with: {api_key[:5]}...")

try:
    client = OpenAI(
        api_key=api_key
    )
    # Configure the httpx client with a longer timeout
    import httpx
    try:
        client.http_client = httpx.Client(
            timeout=httpx.Timeout(60.0, connect=30.0, read=30.0, write=30.0, pool=30.0),
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
        )
        print("Configured httpx client with extended timeouts")
    except Exception as e:
        print(f"Warning: Could not configure httpx client: {e}")
    print("OpenAI client initialized successfully")
except Exception as e:
    print(f"Error initializing OpenAI client: {e}")
    import traceback
    print(traceback.format_exc())
