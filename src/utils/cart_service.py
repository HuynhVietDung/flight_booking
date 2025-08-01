"""
Cart and Order management service
"""

from typing import Dict, List, Optional
from .models import Cart, Order, BookingData, OrderStatus, PaymentStatus
from .payment_service import payment_service, PaymentMethod
import uuid


class CartService:
    """Service for managing shopping carts and orders."""
    
    def __init__(self):
        self.carts: Dict[str, Cart] = {}
        self.orders: Dict[str, Order] = {}
    
    def get_or_create_cart(self, user_id: str) -> Cart:
        """Get existing cart for user or create a new one."""
        if user_id not in self.carts:
            self.carts[user_id] = Cart(user_id=user_id)
        return self.carts[user_id]
    
    def create_order_from_booking(self, user_id: str, booking_data: Dict[str, any], 
                                auto_payment: bool = True, payment_method: PaymentMethod = PaymentMethod.CREDIT_CARD) -> Dict[str, any]:
        """Create an order from booking data, add to user's cart, and optionally process payment."""
        # Create BookingData object
        booking = BookingData(
            flight_number=booking_data["flight_number"],
            passenger_name=booking_data["passenger_name"],
            email=booking_data["email"],
            passengers=booking_data["passengers"],
            class_type=booking_data["class_type"],
            total_price=booking_data["total_price"],
            booking_reference=booking_data["booking_ref"],
            status=booking_data["status"]
        )
        
        # Create Order
        order = Order(
            user_id=user_id,
            flight_booking=booking,
            total_amount=booking_data["total_price"],
            currency="USD",
            notes=f"Order created from booking {booking_data['booking_ref']}"
        )
        
        # Store order
        self.orders[order.order_id] = order
        
        # Get or create cart for user
        cart = self.get_or_create_cart(user_id)
        
        # Add order to cart
        cart.add_order(order)
        
        result = {
            "order": order,
            "cart": cart,
            "payment_info": None
        }
        
        # Process payment if auto_payment is enabled
        if auto_payment:
            try:
                # Create payment transaction
                transaction = payment_service.create_payment_transaction(order, payment_method)
                
                # Process payment
                payment_result = payment_service.process_payment(transaction.transaction_id)
                
                if payment_result["success"]:
                    # Update order status
                    order.update_status(OrderStatus.CONFIRMED)
                    order.update_payment_status(PaymentStatus.PAID)
                    
                    # Generate receipt
                    receipt = payment_service.generate_payment_receipt(transaction)
                    
                    result["payment_info"] = {
                        "success": True,
                        "transaction_id": transaction.transaction_id,
                        "amount": transaction.amount,
                        "payment_method": payment_method.value,
                        "receipt": receipt,
                        "message": "Payment processed successfully"
                    }
                else:
                    result["payment_info"] = {
                        "success": False,
                        "transaction_id": transaction.transaction_id,
                        "error": payment_result.get("error_message", "Payment failed"),
                        "message": "Payment processing failed"
                    }
                    
            except Exception as e:
                result["payment_info"] = {
                    "success": False,
                    "error": str(e),
                    "message": "Payment processing error"
                }
        
        return result
    
    def get_user_cart(self, user_id: str) -> Optional[Cart]:
        """Get cart for a specific user."""
        return self.carts.get(user_id)
    
    def get_user_orders(self, user_id: str) -> List[Order]:
        """Get all orders for a specific user."""
        return [order for order in self.orders.values() if order.user_id == user_id]
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """Get order by order ID."""
        return self.orders.get(order_id)
    
    def update_order_status(self, order_id: str, new_status: OrderStatus) -> bool:
        """Update order status."""
        order = self.orders.get(order_id)
        if order:
            order.update_status(new_status)
            return True
        return False
    
    def update_payment_status(self, order_id: str, new_payment_status: PaymentStatus) -> bool:
        """Update payment status."""
        order = self.orders.get(order_id)
        if order:
            order.update_payment_status(new_payment_status)
            return True
        return False
    
    def remove_order_from_cart(self, user_id: str, order_id: str) -> bool:
        """Remove order from user's cart."""
        cart = self.get_user_cart(user_id)
        if cart:
            return cart.remove_order(order_id)
        return False
    
    def checkout_user_cart(self, user_id: str, payment_method: PaymentMethod = PaymentMethod.CREDIT_CARD) -> Dict[str, any]:
        """Process checkout for user's cart with payment processing."""
        cart = self.get_user_cart(user_id)
        if not cart:
            return {"success": False, "message": "No cart found for user"}
        
        if cart.is_empty():
            return {"success": False, "message": "Cart is empty"}
        
        # Process payment for each order
        payment_results = []
        successful_orders = []
        
        for order in cart.orders:
            # Create payment transaction
            transaction = payment_service.create_payment_transaction(order, payment_method)
            
            # Process payment
            payment_result = payment_service.process_payment(transaction.transaction_id)
            
            if payment_result["success"]:
                # Update order status
                order.update_status(OrderStatus.CONFIRMED)
                order.update_payment_status(PaymentStatus.PAID)
                successful_orders.append(order.order_id)
                
                # Generate receipt
                receipt = payment_service.generate_payment_receipt(transaction)
                payment_results.append({
                    "order_id": order.order_id,
                    "transaction_id": transaction.transaction_id,
                    "amount": transaction.amount,
                    "payment_method": payment_method.value,
                    "receipt": receipt
                })
            else:
                payment_results.append({
                    "order_id": order.order_id,
                    "transaction_id": transaction.transaction_id,
                    "error": payment_result.get("error_message", "Payment failed")
                })
        
        return {
            "success": len(successful_orders) > 0,
            "cart_id": cart.cart_id,
            "total_orders": len(cart.orders),
            "successful_payments": len(successful_orders),
            "failed_payments": len(cart.orders) - len(successful_orders),
            "payment_results": payment_results,
            "successful_orders": successful_orders
        }
    
    def get_cart_summary(self, user_id: str) -> Dict[str, any]:
        """Get summary of user's cart."""
        cart = self.get_user_cart(user_id)
        if not cart:
            return {"success": False, "message": "No cart found for user"}
        
        return {
            "success": True,
            "cart_id": cart.cart_id,
            "order_count": cart.get_order_count(),
            "total_amount": cart.get_total_amount(),
            "is_empty": cart.is_empty(),
            "orders": [
                {
                    "order_id": order.order_id,
                    "flight_number": order.flight_booking.flight_number,
                    "passenger_name": order.flight_booking.passenger_name,
                    "total_amount": order.total_amount,
                    "order_status": order.order_status.value,
                    "payment_status": order.payment_status.value
                }
                for order in cart.orders
            ]
        }


# Global instance
cart_service = CartService() 