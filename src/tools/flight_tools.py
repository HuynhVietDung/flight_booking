"""
Flight booking tools for the agent
"""

import random
from typing import Dict, List, Any
from langchain_core.tools import tool
from ..config import settings


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
def book_flight(flight_number: str, passenger_name: str, email: str, passengers: int = 1, class_type: str = "economy") -> str:
    """Book a specific flight for a passenger."""
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

    return f"""✅ Flight booking confirmed!

Flight: {flight_number}
Passenger: {passenger_name}
Email: {email}
Passengers: {passengers}
Class: {class_type}
Total Price: ${total_price:.2f}
Booking Reference: {booking_ref}

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


# Export all tools
flight_tools = [
    search_flights,
    book_flight,
    get_weather,
    get_flight_status,
    get_booking_info,
    cancel_booking
] 