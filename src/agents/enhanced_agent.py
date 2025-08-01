"""
Enhanced Flight Booking Agent with advanced features
"""

from typing import Literal
from langchain_core.messages import AIMessage, HumanMessage
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
import logging

logger = logging.getLogger(__name__)

class EnhancedFlightAgent(BaseFlightAgent):
    """Enhanced flight booking agent with advanced features."""
    
    def __init__(self):
        super().__init__()
        self.intent_parser = JsonOutputParser(pydantic_object=IntentClassification)
        self.booking_parser = JsonOutputParser(pydantic_object=BookingInformation)
    
    def classify_intent(self, state: FlightBookingState) -> FlightBookingState:
        """Enhanced intent classification with confidence scoring."""
        messages = state.get("messages", [])
        
        # logger.info(f"Messages: {messages}")
        recent_messages = []
        for msg in messages[-10:]:
            if isinstance(msg, HumanMessage):
                recent_messages.append("User: " + msg.content[0]['text'])
            elif isinstance(msg, AIMessage) and "Intent:" not in msg.content:
                recent_messages.append("Assistant: " + msg.content)
            else:
                continue
                
        logger.info(f"Recent messages for intent classification: {recent_messages}")
        
        # Combine all recent messages for context
        combined_text = " ".join(recent_messages) if recent_messages else ""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert intent classifier for a flight booking system. 
            Analyze the user's conversation history and classify their intent with high accuracy.
            
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
            
            You MUST respond with ONLY a valid JSON object in this exact format:
            {{
                "intent": "the_classified_intent",
                "confidence": float_number_between_0_and_1,
                "reasoning": "Text summarizes the user's request and MUST have any booking details user explicitly provided"
            }}
            
            Do not include any other text, explanations, or formatting outside the JSON object."""),
            ("user", "Classify the intent from this conversation: {combined_text}")
        ])
        
        chain = prompt | self.llm | self.intent_parser
        
        try:
            result = chain.invoke({"combined_text": combined_text})
            logger.info(f"Intent classification result: {result}")
            return {
                "intent": result["intent"],
                "intent_confidence": result["confidence"],
                "reasoning": result["reasoning"],
                "messages": [AIMessage(content=f"Intent: {result['intent']} (confidence: {result['confidence']:.2f})")]
            }
        except Exception as e:
            # Fallback to simple classification
            logger.error(f"Intent classification failed: {e}")
            return {
                "intent": "general_inquiry",
                "intent_confidence": 0.5,
                "reasoning": "Intent classification failed, defaulting to general inquiry",
                "messages": [AIMessage(content="Intent classification failed, defaulting to general inquiry")]
            }
    
    def collect_booking_info(self, state: FlightBookingState) -> FlightBookingState:
        """Intelligently extract and request missing booking information based on intent reasoning."""
        # logger.info(f"Collecting booking info for state: {state}")
        current_info = state.get("booking_info", {})
        missing_fields = [field for field in current_info if not current_info.get(field)]
        intent = state.get("intent", "")
        user_intent_expansion = state.get("reasoning", "")
        # logger.info(f"User intent expansion: {user_intent_expansion}")
                
        # Use LLM to extract booking information from user's latest message
        extraction_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at extracting flight booking information. 
            Extract any missing booking information mentioned in the user's intent expansion and update the current booking info.
            
            Current booking information: {current_info}
            Missing fields: {missing_fields}
            
            You MUST respond with ONLY a valid JSON object in this exact format:
            {{
                "extracted_info": {{
                    "field_name": "extracted_value",
                    ...
                }},
                "updated_info": {{
                    "field_name": "final_value",
                    ...
                }},
                "user_intent_expansion": "<exactly the input user_intent_expansion text>"
            }}
            
            Do not include any other text, explanations, or formatting outside the JSON object."""),
            ("user", "Extract booking information from the user intent expansion. User intent expansion: {user_intent_expansion}")
        ])
        
        extraction_parser = JsonOutputParser()
        extraction_chain = extraction_prompt | self.llm | extraction_parser
        
        try:
            extraction_result = extraction_chain.invoke({
                "current_info": current_info,
                "missing_fields": missing_fields,
                "user_intent_expansion": user_intent_expansion
            })
            
            logger.info(f"Extraction result: {extraction_result}")
            
            # Update current_info with extracted information
            if extraction_result.get("updated_info"):
                current_info.update(extraction_result["updated_info"])
                logger.info(f"Updated booking info: {current_info}")
                
        except Exception as e:
            logger.error(f"Information extraction failed: {e}")
        
        # Now determine what information is still missing using simple logic
        required_fields = settings.booking.required_fields.get(intent, [])
        missing_fields = [field for field in required_fields if not current_info.get(field)]
        
        logger.info(f"Required fields for {intent}: {required_fields}")
        logger.info(f"Missing fields: {missing_fields}")
        
        if missing_fields:
            # Generate a natural question for the first missing field
            field_names = settings.booking.field_names
            first_missing_field = missing_fields[0]
            
            # Create natural questions based on context
            question_templates = {
                "departure_city": "Where will you be departing from?",
                "arrival_city": "Where would you like to go?",
                "date": "What date would you like to travel?",
                "passenger_name": "What is the passenger's name?",
                "email": "What email address should I use for the booking confirmation?",
                "passengers": "How many passengers will be traveling?",
                "class_type": "What class would you prefer? (economy, business, or first)"
            }
            
            action_template = {
                "departure_city": "show city list",
                "arrival_city": "show city list",
                "date": "show calendar",
                "passenger_name": "show name input",
                "email": "show email input",
                "passengers": "show number input",
                "class_type": "show class type list"
            }
            question = question_templates.get(first_missing_field, f"Could you please provide the {field_names.get(first_missing_field, first_missing_field)}?")
            action = action_template.get(first_missing_field, "show text input")

            return {
                "booking_info": current_info,
                "current_step": "collecting_info",
                "final_response": question,
                "action": {
                    "field": first_missing_field,
                    "action": action,
                    "is_show": True
                },
                "messages": [AIMessage(content=question)]
            }
        else:
            # All information collected
            return {
                "booking_info": current_info,
                "current_step": "info_complete",
                "final_response": "Perfect! I have all the information I need to help you.",
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


def create_flight_booking_agent_graph():
    """Create the enhanced flight booking agent graph."""
    agent = EnhancedFlightAgent()
    return agent.create_graph().compile()