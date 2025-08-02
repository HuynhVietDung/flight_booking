"""
Base agent class for Flight Booking Agent
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph

from src.config import settings
from src.utils import AgentResponse
from src.tools import flight_tools
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.memory import InMemorySaver


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
    
    def compile_graph(self, file_path: str = "data/langgraph_checkpoints.db") -> StateGraph:
        """Compile the agent graph with SQLite checkpointer."""
        if self.graph is None:
            self.graph = self.create_graph()
        
        # Use built-in SQLite checkpointer
        try:
            # Create SQLite connection for checkpoints
            conn = sqlite3.connect(file_path)
            checkpointer = SqliteSaver(conn)
            
            return self.graph.compile(checkpointer=checkpointer)
            
        except ImportError:
            checkpointer = InMemorySaver()
            return self.graph.compile(checkpointer=checkpointer)
    
    def run(self, user_input: str, thread_id: Optional[str] = None, user_id: Optional[str] = None) -> AgentResponse:
        """Run the agent with user input."""
        try:
            # Compile graph if not already compiled
            compiled_graph = self.compile_graph()
            
            # Prepare input
            inputs = {
                "messages": [HumanMessage(content=user_input)]
            }
            
            # Prepare config with thread_id and user_id
            config = {}
            if thread_id or user_id:
                config["configurable"] = {}
                if thread_id:
                    config["configurable"]["thread_id"] = thread_id
                if user_id:
                    config["configurable"]["user_id"] = user_id
            
            # Run the graph with config to ensure checkpointing
            if config:
                result = compiled_graph.invoke(inputs, config=config)
            else:
                # If no config, still run but without checkpointing
                result = compiled_graph.invoke(inputs)
            
            # Create response
            intent_classification = result.get('intent_classification')
            response = AgentResponse(
                success=True,
                intent=intent_classification.intent if intent_classification else 'unknown',
                confidence=intent_classification.confidence if intent_classification else 0.0,
                response=result.get('messages', [{}])[-1].content if result.get('messages') else '',
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
    
    def preprocess_input(self, user_input: str) -> str:
        """Preprocess user input."""
        return user_input.strip()
    
    def postprocess_response(self, response: AgentResponse) -> AgentResponse:
        """Postprocess agent response."""
        # Add any post-processing logic here
        return response 
    