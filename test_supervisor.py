from src.supervisor import SupervisorAgent

def test_supervisor():
    print("Booting up Sentinel System...")
    supervisor = SupervisorAgent()
    
    # 1. Find a customer with an ANOMALY (Cheat mode enabled)
    # We look for a high bill again to make the demo exciting
    high_spenders = supervisor.billing_agent.billing_df[supervisor.billing_agent.billing_df['amount'] > 150]
    if len(high_spenders) > 0:
        target_customer = high_spenders.iloc[0]['customer_id']
    else:
        target_customer = "CUST_0001" # Fallback
        
    print(f"\n--- SCENARIO: Customer {target_customer} complains ---")
    user_query = "My bill is huge! And my internet is very slow in Zone B."
    
    response = supervisor.handle_request(target_customer, user_query)
    
    print("\n" + "="*40)
    print("       FINAL RESPONSE FROM SENTINEL       ")
    print("="*40)
    print(response)
    print("="*40 + "\n")
    
    # Verification Logic
    if "BILLING ALERT" in response and "firmware" in response.lower():
        print("✅ PASS: Supervisor successfully coordinated both agents.")
    else:
        print("❌ FAIL: Supervisor missed one of the issues.")

if __name__ == "__main__":
    test_supervisor()
