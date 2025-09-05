"""
Pydantic schemas for Ruua API
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class OfferRequest(BaseModel):
    """Request schema for creating a loan offer"""
    user_id: str = Field(..., description="Unique user identifier")
    order_amount: float = Field(..., gt=0, description="Order amount in local currency")
    recent_payments: int = Field(..., ge=0, description="Number of recent successful payments")
    failed_payments_last_30_days: int = Field(..., ge=0, description="Failed payments in last 30 days")
    device_country: str = Field(..., description="Country where device is located")
    billing_country: str = Field(..., description="Country for billing address")
    employer_enrolled: bool = Field(..., description="Whether employer is enrolled in salary deduction")
    salary_monthly: Optional[float] = Field(None, ge=0, description="Monthly salary amount")

class OfferResponse(BaseModel):
    """Response schema for loan offer"""
    offer_id: str = Field(..., description="Unique offer identifier")
    status: str = Field(..., description="Offer status: approved, approved_installments, manual_review")
    amount_offered: float = Field(..., description="Amount offered for loan")
    term_months: int = Field(..., description="Loan term in months")
    interest_rate: float = Field(..., description="Annual interest rate percentage")
    monthly_payment: float = Field(..., description="Monthly payment amount")
    reason: str = Field(..., description="Reason for offer decision")

class PayRequest(BaseModel):
    """Request schema for processing payment"""
    offer_id: str = Field(..., description="Offer ID to process payment for")

class PayResponse(BaseModel):
    """Response schema for payment processing"""
    success: bool = Field(..., description="Whether payment was successful")
    transaction_id: str = Field(..., description="Unique transaction identifier")
    message: str = Field(..., description="Payment processing message")

class FraudRequest(BaseModel):
    """Request schema for fraud detection"""
    user_id: str = Field(..., description="User identifier")
    transaction_amount: float = Field(..., gt=0, description="Transaction amount")
    device_country: str = Field(..., description="Device country")
    billing_country: str = Field(..., description="Billing country")
    device_count: int = Field(..., ge=1, description="Number of devices used by user")
    failed_payments_last_30_days: int = Field(..., ge=0, description="Failed payments in last 30 days")

class FraudResponse(BaseModel):
    """Response schema for fraud detection"""
    fraud_check_id: str = Field(..., description="Unique fraud check identifier")
    status: str = Field(..., description="Fraud status: approved, suspicious, flagged")
    fraud_score: int = Field(..., ge=0, le=100, description="Fraud risk score (0-100)")
    flags: List[str] = Field(..., description="List of fraud flags raised")
    action: str = Field(..., description="Recommended action: allow, review, block")
    created_at: str = Field(..., description="Timestamp of fraud check")

class TransactionResponse(BaseModel):
    """Response schema for transaction data"""
    transaction_id: str = Field(..., description="Unique transaction identifier")
    offer_id: str = Field(..., description="Associated offer ID")
    amount: float = Field(..., description="Transaction amount")
    status: str = Field(..., description="Transaction status")
    created_at: str = Field(..., description="Transaction timestamp")

class UserCreate(BaseModel):
    """Schema for creating a new user"""
    user_id: str = Field(..., description="Unique user identifier")
    email: str = Field(..., description="User email address")
    phone: Optional[str] = Field(None, description="User phone number")
    country: str = Field(..., description="User country")

class UserResponse(BaseModel):
    """Response schema for user data"""
    user_id: str = Field(..., description="Unique user identifier")
    email: str = Field(..., description="User email address")
    phone: Optional[str] = Field(None, description="User phone number")
    country: str = Field(..., description="User country")
    created_at: datetime = Field(..., description="User creation timestamp")
    is_verified: bool = Field(..., description="Whether user is KYC verified")
