import httpx
import time

print("Testing connection to OpenAI API...")
try:
    start_time = time.time()
    r = httpx.get('https://api.openai.com/v1/models', 
                  timeout=10, 
                  follow_redirects=True)
    elapsed = time.time() - start_time
    print(f"Status code: {r.status_code}")
    print(f"Response time: {elapsed:.2f} seconds")
except Exception as e:
    print(f"Error: {type(e).__name__}: {str(e)}")

# Try with proxy detection
print("\nChecking for system proxy settings...")
try:
    proxies = httpx.get_environment_proxies()
    print(f"Detected proxies: {proxies}")
    if proxies:
        print("Testing connection with detected proxies...")
        try:
            client = httpx.Client(proxies=proxies, timeout=10)
            r = client.get('https://api.openai.com/v1/models')
            print(f"Status code with proxies: {r.status_code}")
        except Exception as e:
            print(f"Error with proxies: {type(e).__name__}: {str(e)}")
except Exception as e:
    print(f"Error checking proxies: {e}")
