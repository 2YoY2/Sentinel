import pandas as pd
import numpy as np
import os
import sys

class BillingAgent:
    def __init__(self, data_dir=r"C:\Users\hayth\Desktop\SFR\Sentinel\data"):
        self.data_dir = data_dir
        self.billing_file = os.path.join(data_dir, "billing.csv")
        self._load_data()

    def _load_data(self):
        """Loads the billing database."""
        if os.path.exists(self.billing_file):
            self.billing_df = pd.read_csv(self.billing_file)
            # Ensure proper types
            self.billing_df['amount'] = pd.to_numeric(self.billing_df['amount'])
            self.billing_df['date'] = pd.to_datetime(self.billing_df['date'])
        else:
            # Print to stderr if needed
            print(f"Error: Billing data not found at {self.billing_file}", file=sys.stderr)
            raise FileNotFoundError(f"Billing data not found at {self.billing_file}")

    def get_billing_history(self, customer_id):
        """Retrieves billing history for a specific customer."""
        customer_bills = self.billing_df[self.billing_df['customer_id'] == customer_id].copy()
        return customer_bills.sort_values(by='date')

    def detect_billing_anomaly(self, customer_id):
        """
        Analyzes billing history to find anomalies using Z-Score.
        Returns a dict with analysis results.
        """
        history = self.get_billing_history(customer_id)
        
        if len(history) < 3:
            return {
                "status": "INSUFFICIENT_DATA",
                "is_anomaly": False,
                "message": "Not enough billing history to analyze."
            }

        # Get the latest bill
        latest_bill = history.iloc[-1]
        past_bills = history.iloc[:-1] # All bills EXCEPT the latest

        # Calculate Stats on PAST bills
        mean_spend = past_bills['amount'].mean()
        std_dev = past_bills['amount'].std()

        # Avoid division by zero
        if std_dev == 0:
            std_dev = 0.01

        # Calculate Z-Score of the LATEST bill
        z_score = (latest_bill['amount'] - mean_spend) / std_dev
        
        # Threshold: Z-Score > 3 means the bill is 3 standard deviations away (99.7% outlier)
        is_anomaly = z_score > 3

        return {
            "status": "SUCCESS",
            "customer_id": customer_id,
            "latest_bill_date": latest_bill['date'].strftime("%Y-%m-%d"),
            "latest_bill_amount": float(latest_bill['amount']),
            "historical_mean": round(float(mean_spend), 2),
            "z_score": round(float(z_score), 2),
            "is_anomaly": bool(is_anomaly),
            "risk_level": "CRITICAL" if is_anomaly else "NORMAL",
            "message": f"Bill is €{latest_bill['amount']} (Avg: €{round(mean_spend, 2)}). Z-Score: {round(z_score, 2)}"
        }
