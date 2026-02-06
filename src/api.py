from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
import time
from src.supervisor_mcp import SupervisorAgentMCP

# --- DATA CONTRACTS ---
class CustomerRequest(BaseModel):
    customer_id: str
    message: str

class SentinelResponse(BaseModel):
    trace_id: str
    processing_time_ms: float
    response: str
    status: str

app = FastAPI(
    title="SFR Sentinel API (MCP Enabled)",
    description="Autonomous Multi-Agent System using Model Context Protocol",
    version="2.0-mcp"
)

# Global Agent
supervisor = None

@app.on_event("startup")
async def startup_event():
    global supervisor
    print("Loading Sentinel Agents (MCP Client)...")
    supervisor = SupervisorAgentMCP()
    print("Sentinel Agents Ready.")

@app.get("/")
def health_check():
    return {"status": "operational", "system": "SFR Sentinel MCP"}

@app.post("/analyze", response_model=SentinelResponse)
async def analyze_request(req: CustomerRequest):
    trace_id = str(uuid.uuid4())
    start_time = time.time()
    
    print(f"[{trace_id}] Received request for {req.customer_id}")
    
    try:
        # ASYNC Call to Supervisor
        result = await supervisor.handle_request_async(req.customer_id, req.message)
        
        duration = (time.time() - start_time) * 1000
        
        return SentinelResponse(
            trace_id=trace_id,
            processing_time_ms=round(duration, 2),
            response=result,
            status="success"
        )
        
    except Exception as e:
        print(f"[{trace_id}] ERROR: {str(e)}")
        # In prod, log stack trace
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
