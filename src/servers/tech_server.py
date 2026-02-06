from mcp.server.fastmcp import FastMCP
from src.tech_agent import TechnicalAgent

# Create the MCP Server
mcp = FastMCP("Sentinel Technical Service")

# Initialize the RAG agent
# Note: This might take a few seconds to load models, so it happens on server start
agent = TechnicalAgent()

@mcp.tool()
def search_technical_manual(query: str) -> str:
    """
    Searches the technical knowledge base (manuals) for a solution to the user's problem.
    Uses vector search (RAG) to find the most relevant section.
    """
    try:
        return agent.search_manual(query)
    except Exception as e:
        return f"Error searching manual: {str(e)}"

if __name__ == "__main__":
    mcp.run()
