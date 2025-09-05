"""
Ruua - Embedded Finance Platform Backend
FastAPI application implementing loan offers, payments, and fraud detection
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
import json

from database import get_db, engine
from models import Base, User, Offer, Transaction, FraudCheck
from schemas import (
    OfferRequest, OfferResponse, PayRequest, PayResponse, 
    FraudRequest, FraudResponse, TransactionResponse
)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Ruua API",
    description="Embedded Finance Platform - Loan Offers, Payments & Fraud Detection",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for demo (replace with proper database in production)
offers_db = {}
transactions_db = {}
fraud_checks_db = {}

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Ruua API is running", "version": "1.0.0"}

@app.post("/api/offer", response_model=OfferResponse)
async def create_offer(offer_request: OfferRequest, db: Session = Depends(get_db)):
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
            "monthly_payment": offer_request.order_amount * 1.03,
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
    
    # Create database record
    offer = Offer(
        offer_id=offer_id,
        user_id=offer_request.user_id,
        order_amount=offer_request.order_amount,
        status=offer_data["status"],
        amount_offered=offer_data["amount_offered"],
        term_months=offer_data["term_months"],
        interest_rate=offer_data["interest_rate"],
        monthly_payment=offer_data["monthly_payment"],
        created_at=datetime.utcnow()
    )
    db.add(offer)
    db.commit()
    
    return OfferResponse(**offer_data)

@app.post("/api/pay", response_model=PayResponse)
async def process_payment(pay_request: PayRequest, db: Session = Depends(get_db)):
    """
    Process a payment for an approved offer
    """
    
    # Check if offer exists and is approved
    if pay_request.offer_id not in offers_db:
        raise HTTPException(
            status_code=404, 
            detail="Offer not found"
        )
    
    offer = offers_db[pay_request.offer_id]
    if offer["status"] not in ["approved", "approved_installments"]:
        raise HTTPException(
            status_code=400, 
            detail="Offer is not approved for payment"
        )
    
    # Generate transaction ID
    transaction_id = str(uuid.uuid4())
    
    # Create transaction record
    transaction_data = {
        "transaction_id": transaction_id,
        "offer_id": pay_request.offer_id,
        "amount": offer["amount_offered"],
        "status": "completed",
        "created_at": datetime.utcnow().isoformat()
    }
    
    transactions_db[transaction_id] = transaction_data
    
    # Create database record
    transaction = Transaction(
        transaction_id=transaction_id,
        offer_id=pay_request.offer_id,
        amount=offer["amount_offered"],
        status="completed",
        created_at=datetime.utcnow()
    )
    db.add(transaction)
    db.commit()
    
    return PayResponse(
        success=True,
        transaction_id=transaction_id,
        message="Payment processed successfully"
    )

@app.post("/api/fraud-check", response_model=FraudResponse)
async def check_fraud(fraud_request: FraudRequest, db: Session = Depends(get_db)):
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
        "created_at": datetime.utcnow().isoformat()
    }
    
    fraud_checks_db[fraud_check_id] = fraud_data
    
    # Create database record
    fraud_check = FraudCheck(
        fraud_check_id=fraud_check_id,
        user_id=fraud_request.user_id,
        transaction_amount=fraud_request.transaction_amount,
        fraud_score=fraud_score,
        status=status,
        flags=json.dumps(flags),
        created_at=datetime.utcnow()
    )
    db.add(fraud_check)
    db.commit()
    
    return FraudResponse(**fraud_data)

@app.get("/admin/transactions", response_model=List[TransactionResponse])
async def get_transactions(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    Get all transactions for admin dashboard
    """
    
    # Get transactions from database
    transactions = db.query(Transaction).offset(skip).limit(limit).all()
    
    return [
        TransactionResponse(
            transaction_id=t.transaction_id,
            offer_id=t.offer_id,
            amount=t.amount,
            status=t.status,
            created_at=t.created_at.isoformat()
        )
        for t in transactions
    ]

@app.get("/admin/offers")
async def get_offers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all offers for admin dashboard
    """
    offers = db.query(Offer).offset(skip).limit(limit).all()
    
    return [
        {
            "offer_id": o.offer_id,
            "user_id": o.user_id,
            "order_amount": o.order_amount,
            "status": o.status,
            "amount_offered": o.amount_offered,
            "term_months": o.term_months,
            "interest_rate": o.interest_rate,
            "monthly_payment": o.monthly_payment,
            "created_at": o.created_at.isoformat()
        }
        for o in offers
    ]

@app.get("/admin/fraud-checks")
async def get_fraud_checks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all fraud checks for admin dashboard
    """
    fraud_checks = db.query(FraudCheck).offset(skip).limit(limit).all()
    
    return [
        {
            "fraud_check_id": f.fraud_check_id,
            "user_id": f.user_id,
            "transaction_amount": f.transaction_amount,
            "fraud_score": f.fraud_score,
            "status": f.status,
            "flags": json.loads(f.flags) if f.flags else [],
            "created_at": f.created_at.isoformat()
        }
        for f in fraud_checks
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
