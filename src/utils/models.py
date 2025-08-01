"""
Data models for the Flight Booking Agent
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from typing_extensions import TypedDict, Annotated
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from datetime import datetime
from enum import Enum
import uuid


class IntentClassification(BaseModel):
    """Model for intent classification output."""
    intent: str = Field(description="The classified intent")
    confidence: float = Field(description="Confidence score between 0 and 1")
    reasoning: str = Field(description="Brief reasoning for the classification")


class BookingInformation(BaseModel):
    """Model for booking information extraction."""
    departure_city: Optional[str] = Field(description="Departure city", default=None)
    arrival_city: Optional[str] = Field(description="Arrival city", default=None)
    date: Optional[str] = Field(description="Travel date", default=None)
    round_trip: Optional[bool] = Field(description="Is this a round trip? (true/false)", default=None)
    return_date: Optional[str] = Field(description="Return date (required if round_trip is true)", default=None)
    passenger_name: Optional[str] = Field(description="Passenger name", default=None)
    email: Optional[str] = Field(description="Email address", default=None)
    passengers: Optional[int] = Field(description="Number of passengers", default=1)
    class_type: Optional[str] = Field(description="Class type (economy, business, first)", default="economy")


class FlightBookingState(TypedDict):
    """State schema for the flight booking agent."""
    messages: Annotated[list[AnyMessage], add_messages]
    intent_classification: IntentClassification
    booking_info: dict
    conversation_history: list[dict]
    current_step: str
    data: str
    action: dict


class FlightData(BaseModel):
    """Model for flight data."""
    flight_number: str
    departure: str
    arrival: str
    departure_time: str
    arrival_time: str
    price: float
    airline: str
    available_seats: int
    class_type: str = "economy"


class BookingData(BaseModel):
    """Model for booking data."""
    flight_number: str
    passenger_name: str
    email: str
    passengers: int = 1
    class_type: str = "economy"
    total_price: float
    booking_reference: str
    status: str = "confirmed"


class WeatherData(BaseModel):
    """Model for weather data."""
    city: str
    temperature: int
    condition: str
    humidity: str


class AgentResponse(BaseModel):
    """Model for agent response."""
    success: bool
    intent: str
    confidence: float
    response: str
    booking_info: Dict[str, Any] = {}
    error: Optional[str] = None


class ConversationTurn(BaseModel):
    """Model for a conversation turn."""
    user_input: str
    agent_response: str
    intent: str
    confidence: float
    timestamp: str
    booking_info: Dict[str, Any] = {}


class ConversationHistory(BaseModel):
    """Model for conversation history."""
    user_id: str
    turns: List[ConversationTurn] = []
    current_booking_info: Dict[str, Any] = {}
    
    def add_turn(self, turn: ConversationTurn):
        """Add a new turn to the conversation."""
        self.turns.append(turn)
    
    def get_last_turn(self) -> Optional[ConversationTurn]:
        """Get the last conversation turn."""
        return self.turns[-1] if self.turns else None
    
    def get_turn_count(self) -> int:
        """Get the number of turns in the conversation."""
        return len(self.turns) 
    
    def get_summary(self) -> str:
        """Get a summary of the conversation."""
        pass

class OrderStatus(str, Enum):
    """Enum for order status."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class PaymentStatus(str, Enum):
    """Enum for payment status."""
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class Order(BaseModel):
    """Model for an order (đơn hàng)."""
    order_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique order ID")
    user_id: str = Field(description="User ID who created the order")
    flight_booking: BookingData = Field(description="Flight booking information")
    order_status: OrderStatus = Field(default=OrderStatus.PENDING, description="Current order status")
    payment_status: PaymentStatus = Field(default=PaymentStatus.PENDING, description="Payment status")
    created_at: datetime = Field(default_factory=datetime.now, description="Order creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    total_amount: float = Field(description="Total amount for this order")
    currency: str = Field(default="USD", description="Currency for the order")
    notes: Optional[str] = Field(default=None, description="Additional notes for the order")
    
    def update_status(self, new_status: OrderStatus):
        """Update order status."""
        self.order_status = new_status
        self.updated_at = datetime.now()
    
    def update_payment_status(self, new_payment_status: PaymentStatus):
        """Update payment status."""
        self.payment_status = new_payment_status
        self.updated_at = datetime.now()
    
    def is_paid(self) -> bool:
        """Check if order is paid."""
        return self.payment_status == PaymentStatus.PAID
    
    def is_confirmed(self) -> bool:
        """Check if order is confirmed."""
        return self.order_status == OrderStatus.CONFIRMED
    
    def can_cancel(self) -> bool:
        """Check if order can be cancelled."""
        return self.order_status in [OrderStatus.PENDING, OrderStatus.CONFIRMED]


class Cart(BaseModel):
    """Model for shopping cart (giỏ hàng)."""
    cart_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique cart ID")
    user_id: str = Field(description="User ID who owns the cart")
    orders: List[Order] = Field(default_factory=list, description="List of orders in the cart")
    created_at: datetime = Field(default_factory=datetime.now, description="Cart creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    is_active: bool = Field(default=True, description="Whether the cart is active")
    
    def add_order(self, order: Order):
        """Add an order to the cart."""
        self.orders.append(order)
        self.updated_at = datetime.now()
    
    def remove_order(self, order_id: str) -> bool:
        """Remove an order from the cart by order ID."""
        for i, order in enumerate(self.orders):
            if order.order_id == order_id:
                self.orders.pop(i)
                self.updated_at = datetime.now()
                return True
        return False
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """Get an order by order ID."""
        for order in self.orders:
            if order.order_id == order_id:
                return order
        return None
    
    def get_total_amount(self) -> float:
        """Calculate total amount of all orders in the cart."""
        return sum(order.total_amount for order in self.orders)
    
    def get_order_count(self) -> int:
        """Get the number of orders in the cart."""
        return len(self.orders)
    
    def is_empty(self) -> bool:
        """Check if cart is empty."""
        return len(self.orders) == 0
    
    def clear(self):
        """Clear all orders from the cart."""
        self.orders.clear()
        self.updated_at = datetime.now()
    
    def get_pending_orders(self) -> List[Order]:
        """Get all pending orders in the cart."""
        return [order for order in self.orders if order.order_status == OrderStatus.PENDING]
    
    def get_confirmed_orders(self) -> List[Order]:
        """Get all confirmed orders in the cart."""
        return [order for order in self.orders if order.order_status == OrderStatus.CONFIRMED]
    
    def checkout(self) -> Dict[str, Any]:
        """Process checkout for all orders in the cart."""
        if self.is_empty():
            return {"success": False, "message": "Cart is empty"}
        
        total_amount = self.get_total_amount()
        order_count = self.get_order_count()

        return {
            "success": True,
            "cart_id": self.cart_id,
            "total_amount": total_amount,
            "order_count": order_count,
            "orders": [order.order_id for order in self.orders]
        }
