import subprocess
import sys
import json
import threading
import time

class SimpleMCPClient:
    def __init__(self, command, args, cwd=None, env=None):
        self.command = command
        self.args = args
        self.cwd = cwd
        self.env = env
        self.process = None
        self.request_id = 0
        self.lock = threading.Lock()

    def start(self):
        full_cmd = [self.command] + self.args
        print(f"Starting MCP Server: {' '.join(full_cmd)}")
        self.process = subprocess.Popen(
            full_cmd,
            cwd=self.cwd,
            env=self.env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=sys.stderr, # Redirect stderr to main process stderr
            text=True,
            bufsize=1 # Line buffered
        )
        # Verify it started
        time.sleep(1)
        if self.process.poll() is not None:
            raise RuntimeError(f"Server failed to start. Return code: {self.process.returncode}")

    def call_tool(self, tool_name, arguments):
        """
        Sends a JSON-RPC request to execute a tool.
        Docs: https://www.jsonrpc.org/specification
        """
        if not self.process:
            self.start()

        with self.lock:
            self.request_id += 1
            current_id = self.request_id

        # 1. Structure the request
        # MCP uses 'tools/call' method usually, but FastMCP simplifies it. 
        # Actually FastMCP expects specific JSON-RPC method names.
        # Let's try the standard 'call_tool' format or direct method name based on inspection.
        # fastmcp uses 'tools/call'
        
        req = {
            "jsonrpc": "2.0",
            "method": "tools/call", 
            "params": {
                "name": tool_name,
                "arguments": arguments
            },
            "id": current_id
        }
        
        # 2. Send
        try:
            json_str = json.dumps(req)
            self.process.stdin.write(json_str + "\n")
            self.process.stdin.flush()
        except BrokenPipeError:
            raise RuntimeError("Server disconnected.")

        # 3. Receive Response
        # We need to read lines until we find the response with matching ID
        while True:
            line = self.process.stdout.readline()
            if not line:
                raise RuntimeError("Server closed connection.")
            
            try:
                data = json.loads(line)
                if data.get("id") == current_id:
                    # Found our response
                    if "error" in data:
                        raise RuntimeError(f"Tool error: {data['error']}")
                    
                    # Result is in 'result' -> 'content' -> list
                    # Verify structure matches MCP spec
                    return data.get("result", {})
            except json.JSONDecodeError:
                continue # Ignore non-JSON log lines

    def stop(self):
        if self.process:
            self.process.terminate()

class SupervisorAgentMCP:
    def __init__(self):
        print("[Supervisor MCP] Initializing Custom Clients...")
        
        # We need to find the project root
        import os
        project_root = os.getcwd() # Assumption: running from Sentinel root or passed in
        if "Sentinel" not in project_root and os.path.exists("Sentinel"):
            project_root = os.path.join(project_root, "Sentinel")

        env = os.environ.copy()
        env["PYTHONPATH"] = project_root

        self.billing_client = SimpleMCPClient(
            sys.executable, 
            ["-m", "src.servers.billing_server"], 
            cwd=project_root,
            env=env
        )
        
        self.tech_client = SimpleMCPClient(
            sys.executable, 
            ["-m", "src.servers.tech_server"], 
            cwd=project_root,
            env=env
        )
        
        # Start them to warm up
        self.billing_client.start()
        self.tech_client.start()

    async def handle_request_async(self, customer_id, query):
        # We can implement this sync or async, but since our custom client is sync (blocking I/O),
        # we will wrap it or just run it. For this demo, sync is fine inside async def.
        
        print(f"\n[Supervisor MCP] Processing request for {customer_id}: '{query}'")
        response_parts = []
        
        intent_billing = any(word in query.lower() for word in ['bill', 'invoice', 'cost', 'expensive', 'euro', '€'])
        intent_tech = any(word in query.lower() for word in ['internet', 'slow', 'wifi', 'connection', 'cut', 'light', 'box'])
        
        if intent_billing:
            print("[Supervisor MCP] -> Calling Billing Server...")
            try:
                # FastMCP returns result content list
                result = self.billing_client.call_tool("detect_billing_anomaly", {"customer_id": customer_id})
                
                # Extract text
                # Format: {'content': [{'type': 'text', 'text': '...'}]}
                content_text = result['content'][0]['text']
                billing_result = json.loads(content_text)
                
                if billing_result.get('status') == 'SUCCESS':
                    if billing_result.get('is_anomaly'):
                        response_parts.append(f"⚠️ **BILLING ALERT**: {billing_result['message']}")
                    else:
                        response_parts.append(f"✅ **Billing Status**: Normal.")
                else:
                    response_parts.append(f"Storage Error: {billing_result.get('message')}")
            except Exception as e:
                response_parts.append(f"Billing Agent Error: {e}")

        if intent_tech:
            print("[Supervisor MCP] -> Calling Tech Server...")
            try:
                result = self.tech_client.call_tool("search_technical_manual", {"query": query})
                tech_solution = result['content'][0]['text']
                response_parts.append(f"🔧 **Technical Support**: {tech_solution}")
            except Exception as e:
                 response_parts.append(f"Tech Agent Error: {e}")

        return "\n\n".join(response_parts)

if __name__ == "__main__":
    # Test
    import asyncio
    sup = SupervisorAgentMCP()
    print(asyncio.run(sup.handle_request_async("CUST_0001", "My bill is huge and internet is slow")))
