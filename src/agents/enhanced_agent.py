"""
Enhanced Flight Booking Agent with advanced features
"""

from typing import Literal
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import JsonOutputParser
from langgraph.graph import StateGraph, START, END

from src.agents.base_agent import BaseFlightAgent
from src.config import settings
from src.utils import (
    FlightBookingState, 
    IntentClassification, 
    BookingInformation
)


class EnhancedFlightAgent(BaseFlightAgent):
    """Enhanced flight booking agent with advanced features."""
    
    def __init__(self):
        super().__init__()
        self.intent_parser = JsonOutputParser(pydantic_object=IntentClassification)
        self.booking_parser = JsonOutputParser(pydantic_object=BookingInformation)
    
    def classify_intent(self, state: FlightBookingState) -> FlightBookingState:
        """Enhanced intent classification with confidence scoring."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert intent classifier for a flight booking system. 
            Analyze the user's message and classify their intent with high accuracy.
            
            Intent categories:
            - 'book_flight': User wants to book a flight (e.g., "I want to book", "book me a flight")
            - 'search_flights': User wants to search for flights (e.g., "show me flights", "find flights")
            - 'check_weather': User wants weather information (e.g., "weather in", "what's the weather")
            - 'flight_status': User wants flight status (e.g., "flight status", "is my flight on time")
            - 'booking_info': User wants booking information (e.g., "my booking", "booking details")
            - 'cancel_booking': User wants to cancel a booking (e.g., "cancel my flight", "cancel booking")
            - 'general_inquiry': General questions about flights, booking, policies, etc.
            - 'greeting': Simple greetings or casual conversation
            - 'provide_info': User is providing booking information in response to questions
            
            Respond with a JSON object containing:
            - intent: the classified intent
            - confidence: confidence score between 0 and 1
            - reasoning: brief explanation for the classification"""),
            MessagesPlaceholder(variable_name="messages")
        ])
        
        chain = prompt | self.llm | self.intent_parser
        
        try:
            result = chain.invoke({"messages": state["messages"]})
            return {
                "intent": result.intent,
                "intent_confidence": result.confidence,
                "messages": [AIMessage(content=f"Intent: {result.intent} (confidence: {result.confidence:.2f})")]
            }
        except Exception as e:
            # Fallback to simple classification
            return {
                "intent": "general_inquiry",
                "intent_confidence": 0.5,
                "messages": [AIMessage(content="Intent classification failed, defaulting to general inquiry")]
            }
    
    def collect_booking_info(self, state: FlightBookingState) -> FlightBookingState:
        """Intelligently extract and request missing booking information."""
        current_info = state.get("booking_info", {})
        messages = state.get("messages", [])
        
        # Extract information from multiple messages (up to 10, or all if less than 10)
        if messages:
            # Get recent messages (up to 10, excluding intent messages)
            recent_messages = []
            for msg in messages[-10:]:  # Lấy 10 tin nhắn gần nhất
                if hasattr(msg, 'content') and not msg.content.startswith("Intent:"):
                    recent_messages.append(msg.content)
            
            if recent_messages:
                # Combine all recent messages for extraction
                combined_text = " ".join(recent_messages)
                
                extraction_prompt = ChatPromptTemplate.from_messages([
                    ("system", """Extract booking information from the user's conversation history. 
                    Look for departure city, arrival city, date, passenger name, email, number of passengers, and class type.
                    Consider information from all messages in the conversation.
                    Return a JSON object with the extracted information."""),
                    ("user", f"Extract booking info from conversation: {combined_text}")
                ])
                
                extraction_chain = extraction_prompt | self.llm | self.booking_parser
                
                try:
                    extracted_info = extraction_chain.invoke({})
                    # Merge extracted info with existing info
                    for key, value in extracted_info.dict().items():
                        if value is not None:
                            current_info[key] = value
                except Exception:
                    pass  # Continue with existing info if extraction fails
        
        # Define required fields based on intent
        intent = state.get("intent", "")
        required_fields = settings.booking.required_fields.get(intent, [])
        
        missing_fields = [field for field in required_fields if not current_info.get(field)]
        
        if missing_fields:
            # Generate a natural request for the FIRST missing field only
            field_names = settings.booking.field_names
            first_missing_field = missing_fields[0]  # Chỉ lấy field đầu tiên
            
            prompt = f"Could you please provide the {field_names[first_missing_field]} for your flight?"
            
            # Return final response immediately when missing information
            return {
                "booking_info": current_info,
                "current_step": "collecting_info",
                "final_response": prompt,
                "messages": [AIMessage(content=prompt)]
            }
        else:
            # All information collected - continue to process_booking
            return {
                "booking_info": current_info,
                "current_step": "info_complete",
                "messages": [AIMessage(content="Perfect! I have all the information I need to help you.")]
            }
    
    def process_booking(self, state: FlightBookingState) -> FlightBookingState:
        """Enhanced main processing node with better tool handling and conversation flow."""
        intent = state.get("intent", "")
        booking_info = state.get("booking_info", {})
        
        # Create context-aware system prompt
        system_prompts = {
            "book_flight": f"""You are a helpful flight booking assistant. The user wants to book a flight.
            
Current booking information:
- Departure: {booking_info.get('departure_city', 'Not specified')}
- Destination: {booking_info.get('arrival_city', 'Not specified')}
- Date: {booking_info.get('date', 'Not specified')}
- Passenger: {booking_info.get('passenger_name', 'Not specified')}
- Email: {booking_info.get('email', 'Not specified')}
- Passengers: {booking_info.get('passengers', 1)}
- Class: {booking_info.get('class_type', 'economy')}

Use the available tools to help the user complete their booking. First search for flights, then help them book if they choose one.""",
            
            "search_flights": f"""You are a flight search assistant. Help the user find available flights.

Search criteria:
- Departure: {booking_info.get('departure_city', 'Not specified')}
- Destination: {booking_info.get('arrival_city', 'Not specified')}
- Date: {booking_info.get('date', 'Not specified')}
- Passengers: {booking_info.get('passengers', 1)}
- Class: {booking_info.get('class_type', 'economy')}

Use the search_flights tool to find flights based on their requirements.""",
            
            "check_weather": """You are a travel assistant. Help the user get weather information for their destination.
Use the get_weather tool to provide weather updates.""",
            
            "flight_status": """You are a flight status assistant. Help the user check the status of their flight.
Use the get_flight_status tool to provide current flight information.""",
            
            "booking_info": """You are a booking information assistant. Help the user get information about their booking.
Use the get_booking_info tool to provide booking details.""",
            
            "cancel_booking": """You are a booking cancellation assistant. Help the user cancel their flight booking.
Use the cancel_booking tool to process the cancellation."""
        }
        
        system_prompt = system_prompts.get(intent, """You are a helpful flight booking assistant. Answer the user's questions about flights, 
booking, or travel in general. Be friendly and informative. If they want to book or search for flights,
guide them through the process.""")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages")
        ])
        
        # Create the chain with tools
        chain = prompt | self.llm.bind_tools(self.tools)
        
        # Get response from LLM
        response = chain.invoke({"messages": state["messages"]})
        
        # Handle tool calls if any
        if response.tool_calls:
            tool_results = []
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                
                # Find and execute the tool
                tool = self.get_tool_by_name(tool_name)
                if tool:
                    try:
                        result = tool.invoke(tool_args)
                        tool_results.append(f"📋 {tool_name.replace('_', ' ').title()}: {result}")
                    except Exception as e:
                        tool_results.append(f"❌ Error with {tool_name}: {str(e)}")
            
            # Combine response with tool results
            final_response = f"{response.content}\n\n" + "\n".join(tool_results)
        else:
            final_response = response.content
        
        return {
            "final_response": final_response,
            "current_step": "completed",
            "messages": [AIMessage(content=final_response)]
        }
    
    def route_based_on_intent(self, state: FlightBookingState) -> Literal["collect_info", "process_booking", "end"]:
        """Enhanced routing based on intent, confidence, and current state."""
        intent = state.get("intent", "")
        confidence = state.get("intent_confidence", 0.5)
        current_step = state.get("current_step", "")
        
        # If confidence is low, ask for clarification
        if confidence < settings.agent.intent_confidence_threshold and intent not in ["greeting", "general_inquiry"]:
            return "process_booking"  # Let the LLM ask for clarification
        
        # If intent is booking related and we don't have complete info, collect more
        if intent in ["book_flight", "search_flights"]:
            booking_info = state.get("booking_info", {})
            required_fields = settings.booking.required_fields.get(intent, [])
            
            missing_fields = [field for field in required_fields if not booking_info.get(field)]
            
            if missing_fields and current_step != "info_complete":
                return "collect_info"
        
        # If we have all info or it's a simple inquiry, process
        return "process_booking"
    
    def route_after_collect_info(self, state: FlightBookingState) -> Literal["process_booking", "end"]:
        """Route after collect_info based on whether we have complete information."""
        current_step = state.get("current_step", "")
        
        # If we're still collecting info, end the flow (user needs to provide more info)
        if current_step == "collecting_info":
            return "end"
        
        # If info is complete, continue to process_booking
        if current_step == "info_complete":
            return "process_booking"
        
        # Default to process_booking
        return "process_booking"
    
    def create_graph(self) -> StateGraph:
        """Create the enhanced flight booking agent graph."""
        workflow = StateGraph(FlightBookingState)
        
        # Add nodes
        workflow.add_node("classify_intent", self.classify_intent)
        workflow.add_node("collect_info", self.collect_booking_info)
        workflow.add_node("process_booking", self.process_booking)
        
        # Add edges
        workflow.add_edge(START, "classify_intent")
        workflow.add_conditional_edges(
            "classify_intent",
            self.route_based_on_intent,
            {
                "collect_info": "collect_info",
                "process_booking": "process_booking"
            }
        )
        # Add conditional edges from collect_info
        workflow.add_conditional_edges(
            "collect_info",
            self.route_after_collect_info,
            {
                "process_booking": "process_booking",
                "end": END
            }
        )
        workflow.add_edge("process_booking", END)
        
        return workflow 