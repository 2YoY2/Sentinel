from src.billing_agent import BillingAgent
from src.tech_agent import TechnicalAgent

class SupervisorAgent:
    def __init__(self):
        print("[Supervisor] Initializing Team...")
        self.billing_agent = BillingAgent()
        self.tech_agent = TechnicalAgent()
        print("[Supervisor] Team Ready.")

    def handle_request(self, customer_id, query):
        """
        Orchestrates the response to a customer request.
        """
        print(f"\n[Supervisor] Processing request for {customer_id}: '{query}'")
        
        response_parts = []
        
        # --- 1. INTENT DETECTION (Simple Keyword Rule-Based) ---
        intent_billing = any(word in query.lower() for word in ['bill', 'invoice', 'cost', 'expensive', 'euro', '€'])
        intent_tech = any(word in query.lower() for word in ['internet', 'slow', 'wifi', 'connection', 'cut', 'light', 'box'])
        
        # Default to both if unsure, or just say I don't know
        if not intent_billing and not intent_tech:
            return "I'm sorry, I didn't understand your request. Please mention 'bill' or 'internet'."

        # --- 2. DELEGATION ---
        
        # Call Billing Agent?
        if intent_billing:
            print("[Supervisor] -> Delegating to Billing Agent...")
            billing_result = self.billing_agent.detect_billing_anomaly(customer_id)
            
            if billing_result['status'] == 'SUCCESS':
                if billing_result['is_anomaly']:
                    response_parts.append(f"⚠️ **BILLING ALERT**: {billing_result['message']}")
                    response_parts.append("I have flagged this invoice for manual review.")
                else:
                    response_parts.append(f"✅ **Billing Status**: Your latest bill is normal (€{billing_result['latest_bill_amount']}).")
            else:
                response_parts.append("Could not access billing data.")

        # Call Technical Agent?
        if intent_tech:
            print("[Supervisor] -> Delegating to Technical Agent...")
            tech_solution = self.tech_agent.search_manual(query)
            response_parts.append(f"🔧 **Technical Support**: {tech_solution}")

        # --- 3. FINAL SYNTHESIS ---
        final_response = "\n\n".join(response_parts)
        return final_response

if __name__ == "__main__":
    # Test
    sup = SupervisorAgent()
    # Find a customer
    cust_id = sup.billing_agent.billing_df.iloc[0]['customer_id']
    print(sup.handle_request(cust_id, "My bill is too high and internet is slow"))
