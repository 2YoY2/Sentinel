import subprocess
import sys
import json
import time

def test_raw_pipe():
    print("Starting server process...")
    process = subprocess.Popen(
        [sys.executable, "test_server.py"],
        cwd=r"C:\Users\hayth\Desktop\SFR\Sentinel",
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Give it a moment
    time.sleep(1)
    
    # Check if dead
    if process.poll() is not None:
        print(f"Server died immediately! Return code: {process.returncode}")
        print("STDERR:", process.stderr.read())
        return

    print("Server running. Sending JSON-RPC Initialize...")
    # JSON-RPC 2.0 Initialize Request
    req = {
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "1.0"}
        },
        "id": 1
    }
    
    try:
        json_req = json.dumps(req)
        print(f"Sending: {json_req}")
        process.stdin.write(json_req + "\n")
        process.stdin.flush()
        
        print("Waiting for response...")
        response = process.stdout.readline()
        print(f"Received: {response}")
        
    except Exception as e:
        print(f"Error communicating: {e}")
    finally:
        process.terminate()

if __name__ == "__main__":
    test_raw_pipe()
