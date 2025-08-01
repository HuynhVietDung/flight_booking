"""
Flight booking tools for the agent
"""

import random
from typing import Dict, List, Any
from langchain_core.tools import tool
from ..config import settings
from ..utils.cart_service import cart_service
from ..utils.payment_service import PaymentMethod
from ..utils.models import OrderStatus, PaymentStatus


class FlightTools:
    """Collection of flight booking tools."""
    
    def __init__(self):
        self.mock_flights_db = self._initialize_mock_flights()
        self.mock_weather_db = self._initialize_mock_weather()
        self.mock_bookings_db = {}
    
    def _initialize_mock_flights(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize mock flight database."""
        return {
            "routes": {
                "New York-London": [
                    {
                        "flight_number": "FL001",
                        "departure": "New York",
                        "arrival": "London",
                        "departure_time": "08:00",
                        "arrival_time": "20:30",
                        "price": 299.99,
                        "airline": "MockAir",
                        "available_seats": 45
                    },
                    {
                        "flight_number": "FL002",
                        "departure": "New York", 
                        "arrival": "London",
                        "departure_time": "14:30",
                        "arrival_time": "03:00",
                        "price": 399.99,
                        "airline": "MockAir",
                        "available_seats": 32
                    }
                ],
                "Tokyo-Seoul": [
                    {
                        "flight_number": "FL003",
                        "departure": "Tokyo",
                        "arrival": "Seoul", 
                        "departure_time": "09:15",
                        "arrival_time": "11:45",
                        "price": 199.99,
                        "airline": "SkyWay",
                        "available_seats": 28
                    }
                ],
                "Paris-Tokyo": [
                    {
                        "flight_number": "FL004",
                        "departure": "Paris",
                        "arrival": "Tokyo",
                        "departure_time": "10:30", 
                        "arrival_time": "06:00",
                        "price": 599.99,
                        "airline": "GlobalFly",
                        "available_seats": 15
                    }
                ]
            }
        }
    
    def _initialize_mock_weather(self) -> Dict[str, Dict[str, Any]]:
        """Initialize mock weather database."""
        return {
            "New York": {"temp": 22, "condition": "Partly Cloudy", "humidity": "65%"},
            "London": {"temp": 15, "condition": "Rainy", "humidity": "80%"},
            "Paris": {"temp": 18, "condition": "Sunny", "humidity": "55%"},
            "Tokyo": {"temp": 25, "condition": "Clear", "humidity": "70%"},
            "Sydney": {"temp": 28, "condition": "Sunny", "humidity": "60%"},
            "Seoul": {"temp": 20, "condition": "Cloudy", "humidity": "75%"},
            "Berlin": {"temp": 16, "condition": "Rainy", "humidity": "70%"},
            "Rome": {"temp": 24, "condition": "Sunny", "humidity": "50%"}
        }
    
    def _get_route_key(self, departure: str, arrival: str) -> str:
        """Generate route key for flight lookup."""
        return f"{departure}-{arrival}"
    
    def _generate_flight_number(self) -> str:
        """Generate a unique flight number."""
        return f"FL{random.randint(100, 999)}"
    
    def _calculate_price(self, base_price: float, passengers: int, class_type: str) -> float:
        """Calculate total price based on passengers and class type."""
        multipliers = {
            "economy": 1.0,
            "business": 2.5,
            "first": 4.0
        }
        return base_price * passengers * multipliers.get(class_type, 1.0)


@tool
def search_flights(departure_city: str, arrival_city: str, date: str, passengers: int = 1, class_type: str = "economy") -> str:
    """Search for available flights between cities on a specific date."""
    tools = FlightTools()
    
    route_key = tools._get_route_key(departure_city, arrival_city)
    flights = tools.mock_flights_db["routes"].get(route_key, [])
    
    if not flights:
        # Generate mock flights for new routes
        flights = [
            {
                "flight_number": tools._generate_flight_number(),
                "departure": departure_city,
                "arrival": arrival_city,
                "departure_time": "08:00",
                "arrival_time": "10:30",
                "price": random.randint(200, 600),
                "airline": random.choice(settings.mock_data.airlines),
                "available_seats": random.randint(20, 50)
            },
            {
                "flight_number": tools._generate_flight_number(),
                "departure": departure_city,
                "arrival": arrival_city,
                "departure_time": "14:30",
                "arrival_time": "17:00",
                "price": random.randint(200, 600),
                "airline": random.choice(settings.mock_data.airlines),
                "available_seats": random.randint(20, 50)
            }
        ]
    
    result = f"Found {len(flights)} flights from {departure_city} to {arrival_city} on {date} ({class_type} class):\n\n"
    
    for i, flight in enumerate(flights, 1):
        total_price = tools._calculate_price(flight['price'], passengers, class_type)
        result += f"{i}. {flight['airline']} {flight['flight_number']}\n"
        result += f"   Departure: {flight['departure_time']} | Arrival: {flight['arrival_time']}\n"
        result += f"   Base Price: ${flight['price']} | Total ({passengers} pax, {class_type}): ${total_price:.2f}\n"
        result += f"   Available seats: {flight['available_seats']}\n\n"
    
    return result


@tool
def book_flight(flight_number: str, passenger_name: str, email: str, passengers: int = 1, class_type: str = "economy", 
                user_id: str = None) -> str:
    """Book a specific flight for a passenger and create order in cart (payment to be processed separately)."""
    tools = FlightTools()
    
    # Generate booking reference
    booking_ref = f"BK{flight_number}{hash(email) % 10000:04d}"
    
    # Mock pricing calculation
    base_price = random.randint(200, 600)
    total_price = tools._calculate_price(base_price, passengers, class_type)
    
    # Store booking in mock database
    booking_data = {
        "flight_number": flight_number,
        "passenger_name": passenger_name,
        "email": email,
        "passengers": passengers,
        "class_type": class_type,
        "total_price": total_price,
        "booking_ref": booking_ref,
        "status": "confirmed"
    }
    
    tools.mock_bookings_db[booking_ref] = booking_data
    
    # Auto-generate user_id if not provided
    if not user_id:
        user_id = passenger_name + "123"
    
    # Create order and add to cart (no automatic payment)
    order_info = ""
    payment_instructions = ""
    
    if user_id:
        try:
            result = cart_service.create_order_from_booking(
                user_id, 
                booking_data, 
                auto_payment=False  # No automatic payment
            )
            
            order = result["order"]
            cart = result["cart"]
            
            order_info = f"\n📦 Order created and added to cart!\nOrder ID: {order.order_id}\nCart Total: ${cart.get_total_amount():.2f}"
            
            payment_instructions = f"""

💳 Payment Required:
To complete your booking, please process payment for order {order.order_id}.

Next steps:
1. Use 'show_payment_methods' to see available payment options
2. Use 'get_payment_summary' with order_id: {order.order_id} and your chosen payment_method
3. Use 'confirm_payment' to process the payment when ready"""
                    
        except Exception as e:
            order_info = f"\n⚠️ Warning: Could not create order in cart: {str(e)}"

    return f"""✅ Flight booking confirmed!

Flight: {flight_number}
Passenger: {passenger_name}
Email: {email}
Passengers: {passengers}
Class: {class_type}
Total Price: ${total_price:.2f}
Booking Reference: {booking_ref} {order_info} {payment_instructions}

Your booking confirmation has been sent to {email}."""


@tool
def get_weather(city: str) -> str:
    """Get weather information for a city."""
    tools = FlightTools()
    
    weather_data = tools.mock_weather_db.get(city)
    
    if weather_data:
        return f"Weather in {city}: {weather_data['condition']}, {weather_data['temp']}°C, Humidity: {weather_data['humidity']}"
    else:
        # Generate mock weather for unknown cities
        conditions = ["Sunny", "Partly Cloudy", "Cloudy", "Rainy", "Clear"]
        temp = random.randint(15, 30)
        humidity = f"{random.randint(40, 90)}%"
        condition = random.choice(conditions)
        
        return f"Weather in {city}: {condition}, {temp}°C, Humidity: {humidity}"


@tool
def get_flight_status(flight_number: str) -> str:
    """Get the current status of a flight."""
    statuses = ["On time", "Delayed by 15 minutes", "Delayed by 30 minutes", "Cancelled"]
    gates = ["A12", "B8", "C15", "D3", "E7"]
    
    status = random.choice(statuses)
    gate = random.choice(gates)
    
    if "Cancelled" in status:
        return f"Flight {flight_number}: {status}"
    else:
        return f"Flight {flight_number}: {status}, departing from gate {gate}"


@tool
def get_booking_info(booking_reference: str) -> str:
    """Get information about a specific booking."""
    tools = FlightTools()
    
    booking = tools.mock_bookings_db.get(booking_reference)
    
    if booking:
        return f"""Booking Information:
Reference: {booking['booking_ref']}
Flight: {booking['flight_number']}
Passenger: {booking['passenger_name']}
Email: {booking['email']}
Passengers: {booking['passengers']}
Class: {booking['class_type']}
Total Price: ${booking['total_price']:.2f}
Status: {booking['status']}"""
    else:
        return f"Booking reference {booking_reference} not found."


@tool
def cancel_booking(booking_reference: str, email: str) -> str:
    """Cancel a flight booking."""
    tools = FlightTools()
    
    booking = tools.mock_bookings_db.get(booking_reference)
    
    if not booking:
        return f"Booking reference {booking_reference} not found."
    
    if booking['email'] != email:
        return "Email does not match booking. Cannot cancel."
    
    # Update booking status
    booking['status'] = "cancelled"
    
    return f"""✅ Booking cancelled successfully!

Booking Reference: {booking_reference}
Flight: {booking['flight_number']}
Refund Amount: ${booking['total_price']:.2f}

A refund confirmation has been sent to {email}."""


@tool
def get_cart_summary(user_id: str) -> str:
    """Get summary of user's shopping cart."""
    summary = cart_service.get_cart_summary(user_id)
    
    if not summary["success"]:
        return summary["message"]
    
    if summary["is_empty"]:
        return f"🛒 Your cart is empty (Cart ID: {summary['cart_id']})"
    
    result = f"""🛒 Cart Summary (ID: {summary['cart_id']})
Total Orders: {summary['order_count']}
Total Amount: ${summary['total_amount']:.2f}

Orders in Cart:"""
    
    for order in summary["orders"]:
        result += f"""
  • Order {order['order_id'][:8]}...
    Flight: {order['flight_number']}
    Passenger: {order['passenger_name']}
    Amount: ${order['total_amount']:.2f}
    Status: {order['order_status']} | Payment: {order['payment_status']}"""
    
    return result


@tool
def checkout_cart(user_id: str) -> str:
    """Process checkout for user's shopping cart."""
    checkout_result = cart_service.checkout_user_cart(user_id)
    
    if not checkout_result["success"]:
        return checkout_result["message"]
    
    return f"""✅ Checkout completed successfully!

Cart ID: {checkout_result['cart_id']}
Total Orders: {checkout_result['order_count']}
Total Amount: ${checkout_result['total_amount']:.2f}

Order IDs: {', '.join(checkout_result['orders'])}

Payment processing completed. All orders have been confirmed!"""


@tool
def remove_order_from_cart(user_id: str, order_id: str) -> str:
    """Remove an order from user's shopping cart."""
    success = cart_service.remove_order_from_cart(user_id, order_id)
    
    if success:
        cart = cart_service.get_user_cart(user_id)
        return f"""✅ Order removed from cart successfully!

Order ID: {order_id}
Remaining orders in cart: {cart.get_order_count()}
Cart total: ${cart.get_total_amount():.2f}"""
    else:
        return f"❌ Failed to remove order {order_id} from cart. Order not found or cart is empty."


@tool
def get_payment_methods() -> str:
    """Get available payment methods and their details."""
    from ..utils.payment_service import payment_service
    
    methods = payment_service.get_payment_methods()
    result = "Available Payment Methods:\n\n"
    
    for method_enum, details in methods.items():
        result += f"• {details['name']} ({method_enum.value})\n"
        result += f"  Processing Fee: {details['processing_fee']*100:.1f}%\n"
        result += f"  Processing Time: {details['processing_time']}\n\n"
    
    return result


@tool
def get_payment_receipt(transaction_id: str) -> str:
    """Get payment receipt for a specific transaction."""
    from ..utils.payment_service import payment_service
    
    transaction = payment_service.get_transaction(transaction_id)
    if not transaction:
        return f"❌ Transaction {transaction_id} not found."
    
    if not transaction.is_completed():
        return f"❌ Payment not completed for transaction {transaction_id}. Status: {transaction.payment_status.value}"
    
    receipt = payment_service.generate_payment_receipt(transaction)
    if not receipt["success"]:
        return f"❌ Could not generate receipt: {receipt['error']}"
    
    return f"""📄 Payment Receipt

Receipt ID: {receipt['receipt_id']}
Transaction ID: {receipt['transaction_id']}
Order ID: {receipt['order_id']}
User ID: {receipt['user_id']}

Amount: ${receipt['amount']:.2f} {receipt['currency']}
Payment Method: {receipt['payment_method']}
Processing Fee: ${receipt['processing_fee']:.2f}
Payment Date: {receipt['payment_date']}

Receipt URL: {receipt['receipt_url']}
Payment Details:
  Method: {receipt['payment_details']['method_name']}
  Processing Time: {receipt['payment_details']['processing_time']}"""


@tool
def get_user_payment_history(user_id: str) -> str:
    """Get payment history for a specific user."""
    from ..utils.payment_service import payment_service
    
    transactions = payment_service.get_user_transactions(user_id)
    if not transactions:
        return f"📋 No payment history found for user {user_id}."
    
    result = f"📋 Payment History for User {user_id}\n\n"
    
    for i, transaction in enumerate(transactions, 1):
        result += f"{i}. Transaction ID: {transaction.transaction_id}\n"
        result += f"   Order ID: {transaction.order_id}\n"
        result += f"   Amount: ${transaction.amount:.2f} {transaction.currency}\n"
        result += f"   Payment Method: {transaction.payment_method.value}\n"
        result += f"   Status: {transaction.payment_status.value}\n"
        result += f"   Date: {transaction.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        if transaction.is_completed():
            result += f"   Receipt ID: RCPT-{transaction.transaction_id[:8].upper()}\n"
        elif transaction.is_failed():
            result += f"   Error: {transaction.error_message}\n"
        
        result += "\n"
    
    return result


@tool
def refund_payment(transaction_id: str, reason: str = "Customer request") -> str:
    """Process refund for a completed payment."""
    from ..utils.payment_service import payment_service
    
    refund_result = payment_service.refund_payment(transaction_id, reason)
    
    if refund_result["success"]:
        return f"""✅ Refund processed successfully!

Transaction ID: {refund_result['transaction_id']}
Refund Amount: ${refund_result['refund_amount']:.2f} {refund_result['currency']}
Reason: {refund_result['reason']}
Refund Date: {refund_result['refund_date']}"""
    else:
        return f"❌ Refund failed: {refund_result['error']}"


@tool
def show_payment_methods() -> str:
    """Show available payment methods with details for user selection."""
    from ..utils.payment_service import payment_service
    
    methods = payment_service.get_payment_methods()
    result = "💳 Available Payment Methods:\n\n"
    
    for i, (method_enum, details) in enumerate(methods.items(), 1):
        result += f"{i}. {details['name']} ({method_enum.value})\n"
        result += f"   💰 Processing Fee: {details['processing_fee']*100:.1f}%\n"
        result += f"   ⏱️ Processing Time: {details['processing_time']}\n"
        result += f"   📝 Description: "
        
        if method_enum.value == "credit_card":
            result += "Standard credit card payment with instant processing"
        elif method_enum.value == "debit_card":
            result += "Direct debit from your bank account"
        elif method_enum.value == "bank_transfer":
            result += "Direct bank transfer (may take 1-3 business days)"
        elif method_enum.value == "digital_wallet":
            result += "Mobile or digital wallet payment (PayPal, Apple Pay, etc.)"
        elif method_enum.value == "cash":
            result += "Cash payment at our office (no processing fee)"
        
        result += "\n\n"
    
    result += "To proceed with payment, use the 'get_payment_summary' tool with your chosen payment method."
    return result


@tool
def get_payment_summary(order_id: str, payment_method: str) -> str:
    """Get payment summary for an order with chosen payment method."""
    from ..utils.payment_service import payment_service, PaymentMethod
    from ..utils.cart_service import cart_service
    
    # Get order
    order = cart_service.get_order(order_id)
    if not order:
        return f"❌ Order {order_id} not found."
    
    # Validate payment method
    try:
        payment_method_enum = PaymentMethod(payment_method)
    except ValueError:
        return f"❌ Invalid payment method: {payment_method}"
    
    # Get payment method details
    methods = payment_service.get_payment_methods()
    method_details = methods.get(payment_method_enum)
    if not method_details:
        return f"❌ Payment method {payment_method} not available."
    
    # Calculate payment details
    base_amount = order.total_amount
    processing_fee_rate = method_details["processing_fee"]
    processing_fee = base_amount * processing_fee_rate
    total_amount = base_amount + processing_fee
    
    result = f"""💰 Payment Summary

Order Information:
  Order ID: {order.order_id}
  Flight: {order.flight_booking.flight_number}
  Passenger: {order.flight_booking.passenger_name}
  Base Amount: ${base_amount:.2f} {order.currency}

Payment Method: {method_details['name']} ({payment_method})
Processing Fee: ${processing_fee:.2f} ({processing_fee_rate*100:.1f}%)
Processing Time: {method_details['processing_time']}

💵 Total Amount to Pay: ${total_amount:.2f} {order.currency}

To confirm and process payment, use the 'confirm_payment' tool with:
- order_id: {order.order_id}
- payment_method: {payment_method}
- confirm: true"""
    
    return result


@tool
def confirm_payment(order_id: str, payment_method: str, confirm: bool = False) -> str:
    """Confirm and process payment for an order."""
    from ..utils.payment_service import payment_service, PaymentMethod
    from ..utils.cart_service import cart_service
    
    if not confirm:
        return "❌ Payment not confirmed. Set confirm=true to process payment."
    
    # Get order
    order = cart_service.get_order(order_id)
    if not order:
        return f"❌ Order {order_id} not found."
    
    # Validate payment method
    try:
        payment_method_enum = PaymentMethod(payment_method)
    except ValueError:
        return f"❌ Invalid payment method: {payment_method}"
    
    # Check if order is already paid
    if order.is_paid():
        return f"❌ Order {order_id} is already paid. Payment status: {order.payment_status.value}"
    
    try:
        # Create payment transaction
        transaction = payment_service.create_payment_transaction(order, payment_method_enum)
        
        # Process payment
        payment_result = payment_service.process_payment(transaction.transaction_id)
        
        if payment_result["success"]:
            # Update order status
            order.update_status(OrderStatus.CONFIRMED)
            order.update_payment_status(PaymentStatus.PAID)
            
            # Generate receipt
            receipt = payment_service.generate_payment_receipt(transaction)
            
            return f"""✅ Payment Confirmed and Processed Successfully!

Order Information:
  Order ID: {order.order_id}
  Flight: {order.flight_booking.flight_number}
  Passenger: {order.flight_booking.passenger_name}

Payment Details:
  Transaction ID: {transaction.transaction_id}
  Payment Method: {payment_method_enum.value}
  Amount Paid: ${transaction.amount:.2f} {transaction.currency}
  Processing Fee: ${transaction.amount - order.total_amount:.2f}

Receipt Information:
  Receipt ID: {receipt['receipt_id']}
  Receipt URL: {receipt['receipt_url']}
  Payment Date: {receipt['payment_date']}

Your payment has been processed successfully! A receipt has been generated and sent to your email."""
        else:
            return f"""❌ Payment Processing Failed

Order ID: {order.order_id}
Transaction ID: {transaction.transaction_id}
Payment Method: {payment_method_enum.value}
Error: {payment_result.get('error_message', 'Unknown error')}

Please try again or contact customer support."""
            
    except Exception as e:
        return f"❌ Payment processing error: {str(e)}"


@tool
def get_pending_payments(user_id: str) -> str:
    """Get list of pending payments for a user."""
    from ..utils.cart_service import cart_service
    
    cart = cart_service.get_user_cart(user_id)
    if not cart:
        return f"❌ No cart found for user {user_id}."
    
    pending_orders = [order for order in cart.orders if not order.is_paid()]
    
    if not pending_orders:
        return f"✅ All orders for user {user_id} have been paid."
    
    result = f"📋 Pending Payments for User {user_id}\n\n"
    
    for i, order in enumerate(pending_orders, 1):
        result += f"{i}. Order ID: {order.order_id}\n"
        result += f"   Flight: {order.flight_booking.flight_number}\n"
        result += f"   Passenger: {order.flight_booking.passenger_name}\n"
        result += f"   Amount: ${order.total_amount:.2f} {order.currency}\n"
        result += f"   Status: {order.order_status.value}\n"
        result += f"   Payment Status: {order.payment_status.value}\n\n"
    
    result += "To pay for these orders:\n"
    result += "1. Use 'show_payment_methods' to see available options\n"
    result += "2. Use 'get_payment_summary' with order_id and payment_method\n"
    result += "3. Use 'confirm_payment' to process the payment"
    
    return result


@tool
def cancel_pending_payment(order_id: str) -> str:
    """Cancel a pending payment for an order."""
    from ..utils.cart_service import cart_service
    
    order = cart_service.get_order(order_id)
    if not order:
        return f"❌ Order {order_id} not found."
    
    if order.is_paid():
        return f"❌ Cannot cancel payment for order {order_id}. Payment already completed."
    
    # Update order status to cancelled
    order.update_status(OrderStatus.CANCELLED)
    order.update_payment_status(PaymentStatus.CANCELLED)
    
    return f"""✅ Payment Cancelled Successfully

Order ID: {order.order_id}
Flight: {order.flight_booking.flight_number}
Passenger: {order.flight_booking.passenger_name}
Amount: ${order.total_amount:.2f} {order.currency}

The payment for this order has been cancelled. You can re-initiate payment later if needed."""


# Export all tools
flight_tools = [
    search_flights,
    book_flight,
    get_weather,
    get_flight_status,
    get_booking_info,
    cancel_booking,
    get_cart_summary,
    checkout_cart,
    remove_order_from_cart,
    get_payment_methods,
    get_payment_receipt,
    get_user_payment_history,
    refund_payment,
    show_payment_methods,
    get_payment_summary,
    confirm_payment,
    get_pending_payments,
    cancel_pending_payment
] 