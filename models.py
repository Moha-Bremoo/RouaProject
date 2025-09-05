"""
SQLAlchemy models for Ruua database
"""

from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    """User model for storing user information"""
    __tablename__ = "users"
    
    user_id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True)
    country = Column(String, nullable=False)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    offers = relationship("Offer", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    fraud_checks = relationship("FraudCheck", back_populates="user")

class Offer(Base):
    """Offer model for storing loan offers"""
    __tablename__ = "offers"
    
    offer_id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    order_amount = Column(Float, nullable=False)
    status = Column(String, nullable=False)  # approved, approved_installments, manual_review
    amount_offered = Column(Float, nullable=False)
    term_months = Column(Integer, nullable=False)
    interest_rate = Column(Float, nullable=False)
    monthly_payment = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="offers")
    transactions = relationship("Transaction", back_populates="offer")

class Transaction(Base):
    """Transaction model for storing payment transactions"""
    __tablename__ = "transactions"
    
    transaction_id = Column(String, primary_key=True, index=True)
    offer_id = Column(String, ForeignKey("offers.offer_id"), nullable=False)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String, nullable=False)  # pending, completed, failed, refunded
    payment_method = Column(String, nullable=True)  # card, bank_transfer, wallet
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    offer = relationship("Offer", back_populates="transactions")
    user = relationship("User", back_populates="transactions")

class FraudCheck(Base):
    """Fraud check model for storing fraud detection results"""
    __tablename__ = "fraud_checks"
    
    fraud_check_id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    transaction_amount = Column(Float, nullable=False)
    fraud_score = Column(Integer, nullable=False)  # 0-100
    status = Column(String, nullable=False)  # approved, suspicious, flagged
    flags = Column(Text, nullable=True)  # JSON string of fraud flags
    action = Column(String, nullable=False)  # allow, review, block
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="fraud_checks")

class AdminUser(Base):
    """Admin user model for dashboard access"""
    __tablename__ = "admin_users"
    
    admin_id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
