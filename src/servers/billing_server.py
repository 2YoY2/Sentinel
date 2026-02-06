from mcp.server.fastmcp import FastMCP
from src.billing_agent import BillingAgent
import json

# Create the MCP Server
mcp = FastMCP("Sentinel Billing Service")

# Initialize the agent logic (reusing our existing robust class)
agent = BillingAgent()

@mcp.tool()
def get_billing_history(customer_id: str) -> str:
    """Retrieves the billing history for a specific customer ID from the database."""
    try:
        df = agent.get_billing_history(customer_id)
        if df.empty:
            return "No billing history found."
        return df.to_string(index=False)
    except Exception as e:
        return f"Error accessing database: {str(e)}"

@mcp.tool()
def detect_billing_anomaly(customer_id: str) -> str:
    """
    Analyzes the customer's billing history to detect statistical anomalies (spikes).
    Returns a JSON string with the analysis result.
    """
    try:
        result = agent.detect_billing_anomaly(customer_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"status": "ERROR", "message": str(e)})

if __name__ == "__main__":
    # Runs the server using Standard IO (stdin/stdout) for MCP communication
    mcp.run()
