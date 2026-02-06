import requests
import time
import subprocess
import sys
import os

def test_api():
    print("Starting API Server in background...")
    # Start uvicorn as a subprocess
    server_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "src.api:app", "--port", "8000"],
        cwd=r"C:\Users\hayth\Desktop\SFR\Sentinel",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for startup
    print("Waiting 30s for server to boot...")
    time.sleep(30)
    
    try:
        # 1. Health Check
        print("\nTesting Health Check...")
        try:
            resp = requests.get("http://127.0.0.1:8000/")
            print(f"Health Status: {resp.status_code}")
            print(resp.json())
        except Exception as e:
            print(f"Health check failed: {e}")
            return

        # 2. Analyze Request
        print("\nTesting Analysis Endpoint...")
        payload = {
            "customer_id": "CUST_0001",
            "message": "My bill is extremely high and internet is slow"
        }
        resp = requests.post("http://127.0.0.1:8000/analyze", json=payload)
        
        print(f"Status: {resp.status_code}")
        data = resp.json()
        print("Response Body:")
        print(data)
        
        # Verification
        if "trace_id" in data and ("BILLING ALERT" in str(data) or "Technical Support" in str(data)):
            print("\n✅ PASS: API returned a structured multi-agent response.")
        else:
            print(f"\n❌ FAIL: Response missing expected data. Content: {data}")

    finally:
        print("\nStopping Server...")
        server_process.kill()

if __name__ == "__main__":
    # Ensure requests is installed for the test script
    try:
        import requests
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        import requests
        
    test_api()
