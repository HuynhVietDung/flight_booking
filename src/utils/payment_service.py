"""
Payment processing service for flight bookings
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from .models import Order
import uuid
import json


class PaymentMethod(str, Enum):
    """Enum for payment methods."""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    DIGITAL_WALLET = "digital_wallet"
    CASH = "cash"


class PaymentStatus(str, Enum):
    """Enum for payment status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class PaymentTransaction(BaseModel):
    """Model for payment transaction."""
    transaction_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique transaction ID")
    order_id: str = Field(description="Associated order ID")
    user_id: str = Field(description="User ID who made the payment")
    amount: float = Field(description="Payment amount")
    currency: str = Field(default="USD", description="Payment currency")
    payment_method: PaymentMethod = Field(description="Payment method used")
    payment_status: PaymentStatus = Field(default=PaymentStatus.PENDING, description="Payment status")
    created_at: datetime = Field(default_factory=datetime.now, description="Transaction creation time")
    processed_at: Optional[datetime] = Field(default=None, description="Payment processing time")
    payment_details: Dict[str, Any] = Field(default_factory=dict, description="Payment method specific details")
    receipt_url: Optional[str] = Field(default=None, description="Receipt URL")
    error_message: Optional[str] = Field(default=None, description="Error message if payment failed")
    
    def is_completed(self) -> bool:
        """Check if payment is completed."""
        return self.payment_status == PaymentStatus.COMPLETED
    
    def is_failed(self) -> bool:
        """Check if payment failed."""
        return self.payment_status == PaymentStatus.FAILED


class PaymentService:
    """Service for handling payment processing."""
    
    def __init__(self):
        self.transactions: Dict[str, PaymentTransaction] = {}
        self.payment_methods = {
            PaymentMethod.CREDIT_CARD: {
                "name": "Credit Card",
                "processing_fee": 0.029,  # 2.9%
                "processing_time": "instant"
            },
            PaymentMethod.DEBIT_CARD: {
                "name": "Debit Card", 
                "processing_fee": 0.025,  # 2.5%
                "processing_time": "instant"
            },
            PaymentMethod.BANK_TRANSFER: {
                "name": "Bank Transfer",
                "processing_fee": 0.01,  # 1%
                "processing_time": "1-3 business days"
            },
            PaymentMethod.DIGITAL_WALLET: {
                "name": "Digital Wallet",
                "processing_fee": 0.02,  # 2%
                "processing_time": "instant"
            },
            PaymentMethod.CASH: {
                "name": "Cash Payment",
                "processing_fee": 0.0,  # No fee
                "processing_time": "immediate"
            }
        }
    
    def create_payment_transaction(self, order: Order, payment_method: PaymentMethod, 
                                 payment_details: Dict[str, Any] = None) -> PaymentTransaction:
        """Create a new payment transaction for an order."""
        # Calculate processing fee
        processing_fee_rate = self.payment_methods[payment_method]["processing_fee"]
        processing_fee = order.total_amount * processing_fee_rate
        total_amount = order.total_amount + processing_fee
        
        transaction = PaymentTransaction(
            order_id=order.order_id,
            user_id=order.user_id,
            amount=total_amount,
            currency=order.currency,
            payment_method=payment_method,
            payment_details=payment_details or {},
            receipt_url=f"receipts/{order.order_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
        
        self.transactions[transaction.transaction_id] = transaction
        return transaction
    
    def process_payment(self, transaction_id: str) -> Dict[str, Any]:
        """Process a payment transaction."""
        transaction = self.transactions.get(transaction_id)
        if not transaction:
            return {"success": False, "error": "Transaction not found"}
        
        try:
            # Simulate payment processing
            transaction.payment_status = PaymentStatus.PROCESSING
            
            # Simulate processing time
            import time
            time.sleep(0.1)  # Simulate processing delay
            
            # Simulate success/failure (90% success rate)
            import random
            if random.random() < 0.9:
                transaction.payment_status = PaymentStatus.COMPLETED
                transaction.processed_at = datetime.now()
                success = True
                message = "Payment processed successfully"
            else:
                transaction.payment_status = PaymentStatus.FAILED
                transaction.error_message = "Payment declined by bank"
                success = False
                message = "Payment failed"
            
            return {
                "success": success,
                "transaction_id": transaction_id,
                "message": message,
                "amount": transaction.amount,
                "currency": transaction.currency,
                "payment_method": transaction.payment_method.value,
                "status": transaction.payment_status.value,
                "receipt_url": transaction.receipt_url if success else None,
                "error_message": transaction.error_message
            }
            
        except Exception as e:
            transaction.payment_status = PaymentStatus.FAILED
            transaction.error_message = str(e)
            return {
                "success": False,
                "transaction_id": transaction_id,
                "error": str(e)
            }
    
    def generate_payment_receipt(self, transaction: PaymentTransaction) -> Dict[str, Any]:
        """Generate payment receipt information."""
        if not transaction.is_completed():
            return {"success": False, "error": "Payment not completed"}
        
        receipt = {
            "receipt_id": f"RCPT-{transaction.transaction_id[:8].upper()}",
            "transaction_id": transaction.transaction_id,
            "order_id": transaction.order_id,
            "user_id": transaction.user_id,
            "amount": transaction.amount,
            "currency": transaction.currency,
            "payment_method": transaction.payment_method.value,
            "processing_fee": transaction.amount - transaction.amount / (1 + self.payment_methods[transaction.payment_method]["processing_fee"]),
            "payment_date": transaction.processed_at.isoformat() if transaction.processed_at else None,
            "receipt_url": transaction.receipt_url,
            "payment_details": {
                "method_name": self.payment_methods[transaction.payment_method]["name"],
                "processing_time": self.payment_methods[transaction.payment_method]["processing_time"]
            }
        }
        
        return receipt
    
    def get_payment_methods(self) -> Dict[str, Dict[str, Any]]:
        """Get available payment methods with their details."""
        return self.payment_methods
    
    def get_transaction(self, transaction_id: str) -> Optional[PaymentTransaction]:
        """Get transaction by ID."""
        return self.transactions.get(transaction_id)
    
    def get_user_transactions(self, user_id: str) -> List[PaymentTransaction]:
        """Get all transactions for a user."""
        return [t for t in self.transactions.values() if t.user_id == user_id]
    
    def refund_payment(self, transaction_id: str, reason: str = "Customer request") -> Dict[str, Any]:
        """Process refund for a completed payment."""
        transaction = self.transactions.get(transaction_id)
        if not transaction:
            return {"success": False, "error": "Transaction not found"}
        
        if not transaction.is_completed():
            return {"success": False, "error": "Payment not completed, cannot refund"}
        
        # Simulate refund processing
        transaction.payment_status = PaymentStatus.REFUNDED
        transaction.error_message = f"Refunded: {reason}"
        
        return {
            "success": True,
            "transaction_id": transaction_id,
            "refund_amount": transaction.amount,
            "currency": transaction.currency,
            "reason": reason,
            "refund_date": datetime.now().isoformat()
        }


# Global instance
payment_service = PaymentService() 