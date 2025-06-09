import os
import time
import json
from dotenv import load_dotenv

# Load API key from environment
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("Error: No OpenAI API key found in environment")
    exit(1)

print(f"API key available: {bool(api_key)}")
print(f"API key starts with: {api_key[:5]}...\n")

# Method 1: Using the OpenAI client library (as in our current app)
print("===== TEST 1: Using OpenAI Client Library =====")
try:
    from openai import OpenAI
    
    # Create client with extended timeout
    client = OpenAI(api_key=api_key)
    
    # Configure the httpx client with a longer timeout
    import httpx
    client.http_client = httpx.Client(
        timeout=httpx.Timeout(60.0, connect=30.0),
    )
    
    print("Testing OpenAI client connection...")
    start = time.time()
    try:
        models = client.models.list()
        print(f"Success! First model: {models.data[0].id}")
        print(f"Time taken: {time.time() - start:.2f} seconds")
    except Exception as e:
        print(f"Error: {type(e).__name__}: {str(e)}")
        print(f"Time until error: {time.time() - start:.2f} seconds")
except ImportError:
    print("OpenAI Python package not installed")

# Method 2: Using direct HTTP requests (like requests or another HTTP library)
print("\n===== TEST 2: Using Direct HTTP Requests =====")
try:
    import requests
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print("Testing direct HTTP request...")
    start = time.time()
    try:
        response = requests.get(
            "https://api.openai.com/v1/models",
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        print(f"Success! Status code: {response.status_code}")
        print(f"First model: {response.json()['data'][0]['id']}")
        print(f"Time taken: {time.time() - start:.2f} seconds")
    except Exception as e:
        print(f"Error: {type(e).__name__}: {str(e)}")
        print(f"Time until error: {time.time() - start:.2f} seconds")
except ImportError:
    print("Requests package not installed")

# Method 3: Using curl to test network connectivity
print("\n===== TEST 3: Using curl Command Line =====")
print("Testing connection with curl...")
os.system(f'curl -s -o /dev/null -w "Status code: %{{http_code}}\nTime taken: %{{time_total}} seconds\n" -H "Authorization: Bearer {api_key}" https://api.openai.com/v1/models')

# Check if running through any proxies
print("\n===== PROXY INFORMATION =====")
print("HTTP_PROXY environment variable:", os.environ.get("HTTP_PROXY", "Not set"))
print("HTTPS_PROXY environment variable:", os.environ.get("HTTPS_PROXY", "Not set"))
print("NO_PROXY environment variable:", os.environ.get("NO_PROXY", "Not set"))

# Try to get proxy information from the system
print("\nAttempting to get system proxy information...")
try:
    import subprocess
    result = subprocess.run(["scutil", "--proxy"], capture_output=True, text=True)
    print(result.stdout)
except Exception as e:
    print(f"Error checking system proxies: {e}")

# Check network connectivity to other services for comparison
print("\n===== GENERAL CONNECTIVITY CHECK =====")
print("Testing connection to Google...")
os.system('curl -s -o /dev/null -w "Status code: %{http_code}\nTime taken: %{time_total} seconds\n" https://www.google.com')
