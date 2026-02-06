from src.tech_agent import TechnicalAgent

def test_tech_agent():
    print("Initializing Technical Agent (Loading Models & Index in background)...")
    agent = TechnicalAgent()
    
    # Test Case 1: Specific Context (Zone B)
    query = "My internet is very slow and I live in Zone B"
    print(f"\nQuery: '{query}'")
    response = agent.search_manual(query)
    print(f"Result:\n{'-'*20}\n{response}\n{'-'*20}")
    
    if "firmware" in response.lower():
        print("✅ PASS: Correctly retrieved the firmware fix for Zone B.")
    else:
        print("❌ FAIL: Did not find the Zone B firmware issue.")

    # Test Case 2: Different Issue (Red Light)
    query = "The box has a red light on it"
    print(f"\nQuery: '{query}'")
    response = agent.search_manual(query)
    print(f"Result:\n{'-'*20}\n{response}\n{'-'*20}")
    
    if "cable" in response.lower() or "intervention" in response.lower():
        print("✅ PASS: Correctly retrieved the red light fix.")
    else:
        print("❌ FAIL: Did not find red light solution.")

if __name__ == "__main__":
    test_tech_agent()
