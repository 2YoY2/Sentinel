import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import os

# Configuration
NUM_CUSTOMERS = 100
MONTHS_HISTORY = 6
START_DATE = datetime.now() - timedelta(days=30*MONTHS_HISTORY)
OUTPUT_DIR = r"C:\Users\hayth\Desktop\SFR\Sentinel\data"

fake = Faker()
np.random.seed(42)  # For reproducibility

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def generate_customers(n=NUM_CUSTOMERS):
    customers = []
    for i in range(n):
        customers.append({
            "customer_id": f"CUST_{i+1:04d}",
            "name": fake.name(),
            "email": fake.email(),
            "phone": fake.phone_number(),
            "plan_type": random.choice(["Basic", "Standard", "Premium"]),
            "base_cost": random.choice([29.99, 49.99, 79.99]),
            "region": random.choice(["Zone A", "Zone B", "Zone C"])
        })
    return pd.DataFrame(customers)

def generate_billing(customers_df):
    billing_records = []
    
    # Select 5% of customers to have a "Billing Anomaly" in the last month
    anomaly_indices = np.random.choice(customers_df.index, size=int(len(customers_df) * 0.05), replace=False)
    
    for idx, row in customers_df.iterrows():
        customer_id = row["customer_id"]
        base_cost = row["base_cost"]
        
        for m in range(MONTHS_HISTORY):
            # Month calculation
            bill_date = START_DATE + timedelta(days=30*m)
            month_str = bill_date.strftime("%Y-%m")
            
            # Normal random variation (+/- 5%)
            variation = np.random.uniform(-0.05, 0.05)
            amount = base_cost * (1 + variation)
            
            # Label
            is_anomaly = False
            
            # If this is an anomaly customer AND it's the last month (most recent bill)
            if idx in anomaly_indices and m == MONTHS_HISTORY - 1:
                amount = amount * 3.5  # HUGE spike
                is_anomaly = True
            
            billing_records.append({
                "billing_id": f"BILL_{customer_id}_{month_str}",
                "customer_id": customer_id,
                "date": bill_date.strftime("%Y-%m-%d"),
                "amount": round(amount, 2),
                "is_anomaly_truth": is_anomaly # Hidden label for verification
            })
            
    return pd.DataFrame(billing_records)

def generate_usage(customers_df):
    usage_records = []
    
    # Select 10% of customers to have "Weak Signal" (Usage Drop) -> Churn Risk
    churn_risk_indices = np.random.choice(customers_df.index, size=int(len(customers_df) * 0.10), replace=False)
    
    for idx, row in customers_df.iterrows():
        customer_id = row["customer_id"]
        
        # Base usage between 5GB and 50GB daily (avg)
        avg_daily_usage = np.random.uniform(5, 50)
        
        # Simulate last 90 days
        for day in range(90):
            date = datetime.now() - timedelta(days=90-day)
            
            usage = np.random.normal(avg_daily_usage, 2) # Normal noise
            
            # If churn risk, gradually reduce usage over time
            if idx in churn_risk_indices:
                # Factor decreases from 1.0 down to 0.2 over 90 days
                decline_factor = 1 - (day / 90) * 0.8  
                usage = usage * decline_factor
            
            usage = max(0, usage) # No negative usage
            
            usage_records.append({
                "customer_id": customer_id,
                "date": date.strftime("%Y-%m-%d"),
                "data_usage_gb": round(usage, 2),
                "is_churn_risk_truth": (idx in churn_risk_indices) # Hidden label
            })
            
    return pd.DataFrame(usage_records)

def main():
    ensure_dir(OUTPUT_DIR)
    print("Generating Customers...")
    customers_df = generate_customers()
    customers_df.to_csv(os.path.join(OUTPUT_DIR, "customers.csv"), index=False)
    
    print("Generating Billing History...")
    billing_df = generate_billing(customers_df)
    billing_df.to_csv(os.path.join(OUTPUT_DIR, "billing.csv"), index=False)
    
    print("Generating Usage Data (Weak Signals)...")
    usage_df = generate_usage(customers_df)
    usage_df.to_csv(os.path.join(OUTPUT_DIR, "usage.csv"), index=False)
    
    print(f"Data generation complete! Files saved to {OUTPUT_DIR}")
    print(f"- Customers: {len(customers_df)}")
    print(f"- Billing Records: {len(billing_df)}")
    print(f"- Usage Records: {len(usage_df)}")

if __name__ == "__main__":
    main()
