from src.billing_agent import BillingAgent
import pandas as pd

def test_billing_agent():
    print("Initializing Billing Agent...")
    agent = BillingAgent()
    
    # 1. FIND A KNOWN ANOMALY (Cheat by looking at the data)
    # in generator.py, anomalies were ~3.5x base cost. 
    # Let's find a bill > 100 which is likely an anomaly for our data distribution
    anomaly_candidates = agent.billing_df[agent.billing_df['amount'] > 120]
    
    if len(anomaly_candidates) == 0:
        print("WARNING: No obvious anomalies found in data to test against.")
        return

    # Pick the first one
    anomaly_customer_id = anomaly_candidates.iloc[0]['customer_id']
    print(f"\nTesting ANOMALY Detection on Customer: {anomaly_customer_id}")
    
    result = agent.detect_billing_anomaly(anomaly_customer_id)
    print(result)
    
    if result['is_anomaly']:
        print("✅ PASS: Agent correctly detected the high bill.")
    else:
        print("❌ FAIL: Agent missed the anomaly.")

    # 2. FIND A NORMAL CUSTOMER
    # Pick a customer who is NOT in the anomaly list
    normal_candidates = agent.billing_df[~agent.billing_df['customer_id'].isin(anomaly_candidates['customer_id'])]
    normal_customer_id = normal_candidates.iloc[0]['customer_id']
    
    print(f"\nTesting NORMAL Detection on Customer: {normal_customer_id}")
    result_normal = agent.detect_billing_anomaly(normal_customer_id)
    print(result_normal)
    
    if not result_normal['is_anomaly']:
        print("✅ PASS: Agent correctly ignored normal billing.")
    else:
        print("❌ FAIL: Agent flagged a normal bill as anomaly (False Positive).")

if __name__ == "__main__":
    test_billing_agent()
