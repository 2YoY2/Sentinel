import asyncio
from src.supervisor_mcp import SupervisorAgentMCP

async def test_supervisor_mcp():
    print("Booting up Sentinel System (MCP Mode)...")
    supervisor = SupervisorAgentMCP()
    
    # Customer ID (hardcoded for now as we don't have direct access to billing_agent inside supervisor client)
    target_customer = "CUST_0001" 
        
    print(f"\n--- SCENARIO: Customer {target_customer} complains ---")
    user_query = "My bill is huge! And my internet is very slow in Zone B."
    
    print("Sending request to Supervisor (Async)...")
    try:
        response = await supervisor.handle_request_async(target_customer, user_query)
    except Exception as e:
        print(f"CRITICAL ERROR in handle_request_async: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "="*40)
    print("       FINAL RESPONSE FROM SENTINEL (MCP)       ")
    print("="*40)
    print(response)
    print("="*40 + "\n")

if __name__ == "__main__":
    asyncio.run(test_supervisor_mcp())
