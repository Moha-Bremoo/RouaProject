"""
Ruua - Embedded Finance Platform Business Logic
Core functions for loan offers, payments, and fraud detection
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any
import json

# ============================================================================
# DATA MODELS (Simplified)
# ============================================================================

class OfferRequest:
    """Request data for creating a loan offer"""
    def __init__(self, user_id: str, order_amount: float, recent_payments: int, 
                 failed_payments_last_30_days: int, device_country: str, 
                 billing_country: str, employer_enrolled: bool, salary_monthly: float = None):
        self.user_id = user_id
        self.order_amount = order_amount
        self.recent_payments = recent_payments
        self.failed_payments_last_30_days = failed_payments_last_30_days
        self.device_country = device_country
        self.billing_country = billing_country
        self.employer_enrolled = employer_enrolled
        self.salary_monthly = salary_monthly

class PayRequest:
    """Request data for processing payment"""
    def __init__(self, offer_id: str):
        self.offer_id = offer_id

class FraudRequest:
    """Request data for fraud detection"""
    def __init__(self, user_id: str, transaction_amount: float, device_country: str,
                 billing_country: str, device_count: int, failed_payments_last_30_days: int):
        self.user_id = user_id
        self.transaction_amount = transaction_amount
        self.device_country = device_country
        self.billing_country = billing_country
        self.device_count = device_count
        self.failed_payments_last_30_days = failed_payments_last_30_days

# ============================================================================
# IN-MEMORY STORAGE
# ============================================================================

offers_db = {}
transactions_db = {}
fraud_checks_db = {}

# ============================================================================
# CORE BUSINESS LOGIC FUNCTIONS
# ============================================================================

def create_offer(offer_request: OfferRequest) -> Dict[str, Any]:
    """
    Create a loan offer based on user data and business rules
    
    Business Rules:
    - order_amount <= 200: approve (amount_offered=order_amount, term_months=1, interest_rate=3%)
    - order_amount <= 1000 and recent_payments >= 3: approve_installments (term_months=2, interest_rate=4%)
    - else: refer_manual_review
    """
    
    # Generate unique offer ID
    offer_id = str(uuid.uuid4())
    
    # Apply business rules
    if offer_request.order_amount <= 200:
        # Small amount - instant approval
        offer_data = {
            "offer_id": offer_id,
            "status": "approved",
            "amount_offered": offer_request.order_amount,
            "term_months": 1,
            "interest_rate": 3.0,
            "monthly_payment": round(offer_request.order_amount * 1.03, 2),
            "reason": "Small amount instant approval"
        }
    elif offer_request.order_amount <= 1000 and offer_request.recent_payments >= 3:
        # Medium amount with payment history - installment approval
        monthly_rate = 1 + (4.0 / 100 / 12)  # 4% annual rate
        monthly_payment = offer_request.order_amount * (monthly_rate ** 2) / 2
        offer_data = {
            "offer_id": offer_id,
            "status": "approved_installments",
            "amount_offered": offer_request.order_amount,
            "term_months": 2,
            "interest_rate": 4.0,
            "monthly_payment": round(monthly_payment, 2),
            "reason": "Good payment history - installment approval"
        }
    else:
        # Large amount or insufficient history - manual review
        offer_data = {
            "offer_id": offer_id,
            "status": "manual_review",
            "amount_offered": 0,
            "term_months": 0,
            "interest_rate": 0.0,
            "monthly_payment": 0.0,
            "reason": "Requires manual review due to amount or insufficient payment history"
        }
    
    # Store offer
    offers_db[offer_id] = offer_data
    
    return offer_data

def process_payment(pay_request: PayRequest) -> Dict[str, Any]:
    """
    Process a payment for an approved offer
    """
    
    # Check if offer exists and is approved
    if pay_request.offer_id not in offers_db:
        return {
            "success": False,
            "transaction_id": None,
            "message": "Offer not found"
        }
    
    offer = offers_db[pay_request.offer_id]
    if offer["status"] not in ["approved", "approved_installments"]:
        return {
            "success": False,
            "transaction_id": None,
            "message": "Offer is not approved for payment"
        }
    
    # Generate transaction ID
    transaction_id = str(uuid.uuid4())
    
    # Create transaction record
    transaction_data = {
        "transaction_id": transaction_id,
        "offer_id": pay_request.offer_id,
        "amount": offer["amount_offered"],
        "status": "completed",
        "created_at": datetime.now().isoformat()
    }
    
    transactions_db[transaction_id] = transaction_data
    
    return {
        "success": True,
        "transaction_id": transaction_id,
        "message": "Payment processed successfully"
    }

def check_fraud(fraud_request: FraudRequest) -> Dict[str, Any]:
    """
    Perform fraud detection checks
    """
    
    fraud_score = 0
    flags = []
    
    # Check 1: Device/Billing country mismatch
    if fraud_request.device_country != fraud_request.billing_country:
        fraud_score += 30
        flags.append("Device and billing country mismatch")
    
    # Check 2: High number of failed payments
    if fraud_request.failed_payments_last_30_days > 3:
        fraud_score += 40
        flags.append("High number of failed payments in last 30 days")
    
    # Check 3: Unusual transaction amount
    if fraud_request.transaction_amount > 5000:
        fraud_score += 20
        flags.append("Unusual high transaction amount")
    
    # Check 4: Multiple devices
    if fraud_request.device_count > 3:
        fraud_score += 25
        flags.append("Multiple devices detected")
    
    # Determine fraud status
    if fraud_score >= 50:
        status = "flagged"
        action = "block"
    elif fraud_score >= 30:
        status = "suspicious"
        action = "review"
    else:
        status = "approved"
        action = "allow"
    
    # Generate fraud check ID
    fraud_check_id = str(uuid.uuid4())
    
    fraud_data = {
        "fraud_check_id": fraud_check_id,
        "status": status,
        "fraud_score": fraud_score,
        "flags": flags,
        "action": action,
        "created_at": datetime.now().isoformat()
    }
    
    fraud_checks_db[fraud_check_id] = fraud_data
    
    return fraud_data

def get_all_transactions() -> List[Dict[str, Any]]:
    """Get all transactions"""
    return list(transactions_db.values())

def get_all_offers() -> List[Dict[str, Any]]:
    """Get all offers"""
    return list(offers_db.values())

def get_all_fraud_checks() -> List[Dict[str, Any]]:
    """Get all fraud checks"""
    return list(fraud_checks_db.values())

# ============================================================================
# TEST FUNCTIONS
# ============================================================================

def test_loan_offers():
    """Test loan offer creation with different scenarios"""
    print("🧪 Testing Loan Offer Creation...")
    print("=" * 50)
    
    # Test Case 1: Small amount (should be approved)
    print("\n1. Small Amount Test ($150)")
    offer1 = create_offer(OfferRequest(
        user_id="user001",
        order_amount=150.0,
        recent_payments=1,
        failed_payments_last_30_days=0,
        device_country="US",
        billing_country="US",
        employer_enrolled=False,
        salary_monthly=2000.0
    ))
    print(f"   Status: {offer1['status']}")
    print(f"   Amount Offered: ${offer1['amount_offered']}")
    print(f"   Reason: {offer1['reason']}")
    
    # Test Case 2: Medium amount with good history (should be approved with installments)
    print("\n2. Medium Amount with Good History Test ($800)")
    offer2 = create_offer(OfferRequest(
        user_id="user002",
        order_amount=800.0,
        recent_payments=5,
        failed_payments_last_30_days=0,
        device_country="US",
        billing_country="US",
        employer_enrolled=True,
        salary_monthly=4000.0
    ))
    print(f"   Status: {offer2['status']}")
    print(f"   Amount Offered: ${offer2['amount_offered']}")
    print(f"   Monthly Payment: ${offer2['monthly_payment']}")
    print(f"   Reason: {offer2['reason']}")
    
    # Test Case 3: Large amount (should require manual review)
    print("\n3. Large Amount Test ($2000)")
    offer3 = create_offer(OfferRequest(
        user_id="user003",
        order_amount=2000.0,
        recent_payments=2,
        failed_payments_last_30_days=1,
        device_country="US",
        billing_country="US",
        employer_enrolled=False,
        salary_monthly=3000.0
    ))
    print(f"   Status: {offer3['status']}")
    print(f"   Amount Offered: ${offer3['amount_offered']}")
    print(f"   Reason: {offer3['reason']}")
    
    return [offer1, offer2, offer3]

def test_payments(offers):
    """Test payment processing"""
    print("\n\n💳 Testing Payment Processing...")
    print("=" * 50)
    
    # Test payment for approved offer
    if offers[0]['status'] == 'approved':
        print(f"\n1. Processing payment for offer: {offers[0]['offer_id']}")
        payment1 = process_payment(PayRequest(offers[0]['offer_id']))
        print(f"   Success: {payment1['success']}")
        print(f"   Transaction ID: {payment1['transaction_id']}")
        print(f"   Message: {payment1['message']}")
    
    # Test payment for installment offer
    if offers[1]['status'] == 'approved_installments':
        print(f"\n2. Processing payment for installment offer: {offers[1]['offer_id']}")
        payment2 = process_payment(PayRequest(offers[1]['offer_id']))
        print(f"   Success: {payment2['success']}")
        print(f"   Transaction ID: {payment2['transaction_id']}")
        print(f"   Message: {payment2['message']}")
    
    # Test payment for non-approved offer
    if offers[2]['status'] == 'manual_review':
        print(f"\n3. Attempting payment for manual review offer: {offers[2]['offer_id']}")
        payment3 = process_payment(PayRequest(offers[2]['offer_id']))
        print(f"   Success: {payment3['success']}")
        print(f"   Message: {payment3['message']}")

def test_fraud_detection():
    """Test fraud detection with different scenarios"""
    print("\n\n🕵️ Testing Fraud Detection...")
    print("=" * 50)
    
    # Test Case 1: Clean transaction (should be approved)
    print("\n1. Clean Transaction Test")
    fraud1 = check_fraud(FraudRequest(
        user_id="user001",
        transaction_amount=100.0,
        device_country="US",
        billing_country="US",
        device_count=1,
        failed_payments_last_30_days=0
    ))
    print(f"   Status: {fraud1['status']}")
    print(f"   Fraud Score: {fraud1['fraud_score']}")
    print(f"   Action: {fraud1['action']}")
    print(f"   Flags: {fraud1['flags']}")
    
    # Test Case 2: Suspicious transaction (country mismatch)
    print("\n2. Suspicious Transaction Test (Country Mismatch)")
    fraud2 = check_fraud(FraudRequest(
        user_id="user002",
        transaction_amount=500.0,
        device_country="US",
        billing_country="CA",
        device_count=2,
        failed_payments_last_30_days=1
    ))
    print(f"   Status: {fraud2['status']}")
    print(f"   Fraud Score: {fraud2['fraud_score']}")
    print(f"   Action: {fraud2['action']}")
    print(f"   Flags: {fraud2['flags']}")
    
    # Test Case 3: High-risk transaction (multiple red flags)
    print("\n3. High-Risk Transaction Test")
    fraud3 = check_fraud(FraudRequest(
        user_id="user003",
        transaction_amount=10000.0,
        device_country="US",
        billing_country="MX",
        device_count=5,
        failed_payments_last_30_days=8
    ))
    print(f"   Status: {fraud3['status']}")
    print(f"   Fraud Score: {fraud3['fraud_score']}")
    print(f"   Action: {fraud3['action']}")
    print(f"   Flags: {fraud3['flags']}")

def test_admin_functions():
    """Test admin dashboard functions"""
    print("\n\n📊 Testing Admin Functions...")
    print("=" * 50)
    
    print(f"\nTotal Offers: {len(get_all_offers())}")
    print(f"Total Transactions: {len(get_all_transactions())}")
    print(f"Total Fraud Checks: {len(get_all_fraud_checks())}")
    
    print("\nRecent Offers:")
    for offer in get_all_offers()[-3:]:  # Show last 3 offers
        print(f"  - {offer['offer_id'][:8]}... | {offer['status']} | ${offer['amount_offered']}")

def run_all_tests():
    """Run all test functions"""
    print("🚀 Ruua Embedded Finance Platform - Function Testing")
    print("=" * 60)
    
    # Clear previous data
    global offers_db, transactions_db, fraud_checks_db
    offers_db.clear()
    transactions_db.clear()
    fraud_checks_db.clear()
    
    # Run tests
    offers = test_loan_offers()
    test_payments(offers)
    test_fraud_detection()
    test_admin_functions()
    
    print("\n\n✅ All tests completed successfully!")
    print("=" * 60)

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    run_all_tests()