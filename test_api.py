"""
Test suite for Ruua API endpoints
"""

import pytest
import httpx
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root_endpoint():
    """Test health check endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "Ruua API is running" in response.json()["message"]

def test_create_offer_instant_approval():
    """Test loan offer creation with instant approval"""
    offer_data = {
        "user_id": "test_user_1",
        "order_amount": 150.0,
        "recent_payments": 5,
        "failed_payments_last_30_days": 0,
        "device_country": "US",
        "billing_country": "US",
        "employer_enrolled": True,
        "salary_monthly": 5000.0
    }
    
    response = client.post("/api/offer", json=offer_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "approved"
    assert data["amount_offered"] == 150.0
    assert data["term_months"] == 1
    assert data["interest_rate"] == 3.0

def test_create_offer_installment_approval():
    """Test loan offer creation with installment approval"""
    offer_data = {
        "user_id": "test_user_2",
        "order_amount": 800.0,
        "recent_payments": 5,
        "failed_payments_last_30_days": 0,
        "device_country": "US",
        "billing_country": "US",
        "employer_enrolled": True,
        "salary_monthly": 5000.0
    }
    
    response = client.post("/api/offer", json=offer_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "approved_installments"
    assert data["amount_offered"] == 800.0
    assert data["term_months"] == 2
    assert data["interest_rate"] == 4.0

def test_create_offer_manual_review():
    """Test loan offer creation requiring manual review"""
    offer_data = {
        "user_id": "test_user_3",
        "order_amount": 1500.0,
        "recent_payments": 1,
        "failed_payments_last_30_days": 2,
        "device_country": "US",
        "billing_country": "US",
        "employer_enrolled": False,
        "salary_monthly": 3000.0
    }
    
    response = client.post("/api/offer", json=offer_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "manual_review"
    assert data["amount_offered"] == 0.0

def test_process_payment():
    """Test payment processing"""
    # First create an offer
    offer_data = {
        "user_id": "test_user_4",
        "order_amount": 100.0,
        "recent_payments": 3,
        "failed_payments_last_30_days": 0,
        "device_country": "US",
        "billing_country": "US",
        "employer_enrolled": True,
        "salary_monthly": 4000.0
    }
    
    offer_response = client.post("/api/offer", json=offer_data)
    offer_id = offer_response.json()["offer_id"]
    
    # Process payment
    payment_data = {"offer_id": offer_id}
    response = client.post("/api/pay", json=payment_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "transaction_id" in data

def test_fraud_check_approved():
    """Test fraud check with low risk"""
    fraud_data = {
        "user_id": "test_user_5",
        "transaction_amount": 200.0,
        "device_country": "US",
        "billing_country": "US",
        "device_count": 1,
        "failed_payments_last_30_days": 0
    }
    
    response = client.post("/api/fraud-check", json=fraud_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "approved"
    assert data["fraud_score"] < 30

def test_fraud_check_flagged():
    """Test fraud check with high risk"""
    fraud_data = {
        "user_id": "test_user_6",
        "transaction_amount": 1000.0,
        "device_country": "US",
        "billing_country": "CA",  # Country mismatch
        "device_count": 5,  # Multiple devices
        "failed_payments_last_30_days": 5  # High failed payments
    }
    
    response = client.post("/api/fraud-check", json=fraud_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "flagged"
    assert data["fraud_score"] >= 50
    assert len(data["flags"]) > 0

def test_get_transactions():
    """Test admin transactions endpoint"""
    response = client.get("/admin/transactions")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_offers():
    """Test admin offers endpoint"""
    response = client.get("/admin/offers")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_fraud_checks():
    """Test admin fraud checks endpoint"""
    response = client.get("/admin/fraud-checks")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

if __name__ == "__main__":
    pytest.main([__file__])
