"""
Base agent class for Flight Booking Agent
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph

from src.config import settings
from src.utils import AgentResponse, IntentClassification
from src.tools import flight_tools


class BaseAgent(ABC):
    """Base class for flight booking agents."""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.llm.model,
            temperature=settings.llm.temperature,
            max_tokens=settings.llm.max_tokens
        )
        self.processed_llm = ChatOpenAI(
            model=settings.llm.model,
            temperature=0.1,  
            disable_streaming=True
        )
        self.tools = flight_tools
        self.graph = None
    
    @abstractmethod
    def create_graph(self) -> StateGraph:
        """Create the agent graph. Must be implemented by subclasses."""
        pass
    
    def compile_graph(self) -> StateGraph:
        """Compile the agent graph."""
        if self.graph is None:
            self.graph = self.create_graph()
        return self.graph.compile()
    
    def run(self, user_input: str, thread_id: Optional[str] = None) -> AgentResponse:
        """Run the agent with user input."""
        try:
            # Compile graph if not already compiled
            compiled_graph = self.compile_graph()
            
            # Prepare input
            inputs = {
                "messages": [HumanMessage(content=user_input)]
            }
            
            # Run the graph
            result = compiled_graph.invoke(inputs)
            
            # Create response
            intent_classification = result.get('intent_classification')
            response = AgentResponse(
                success=True,
                intent=intent_classification.intent if intent_classification else 'unknown',
                confidence=intent_classification.confidence if intent_classification else 0.0,
                booking_info=result.get('booking_info', {})
            )
            
            return response
            
        except Exception as e:
            return AgentResponse(
                success=False,
                intent='error',
                confidence=0.0,
                response='',
                error=str(e)
            )
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tool names."""
        return [tool.name for tool in self.tools]
    
    def get_tool_by_name(self, tool_name: str):
        """Get a specific tool by name."""
        for tool in self.tools:
            if tool.name == tool_name:
                return tool
        return None
    
    def validate_input(self, user_input: str) -> bool:
        """Validate user input."""
        if not user_input or not user_input.strip():
            return False
        return True
    
    def preprocess_input(self, user_input: str) -> str:
        """Preprocess user input."""
        return user_input.strip()
    
    def postprocess_response(self, response: AgentResponse) -> AgentResponse:
        """Postprocess agent response."""
        # Add any post-processing logic here
        return response 
    