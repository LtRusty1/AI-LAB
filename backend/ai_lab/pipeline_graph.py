"""
Pipeline graph implementation using LangGraph to orchestrate CEO, QA, and Worker agents.
This module provides a robust, type-safe implementation of the agent workflow graph with
dynamic routing, reflection, and error handling.
"""

from typing import Dict, Any, TypedDict, Annotated, Optional, List, Callable
from dataclasses import dataclass
from langgraph.graph import StateGraph
from langchain_openai import ChatOpenAI
from .agents import CEOAgent, QAAgent, WorkerAgent, ReflectionAgent, AGENT_REGISTRY
from .conversation import ConversationManager
import logging
import time
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Rich console
console = Console()

@dataclass
class AgentState:
    """Type-safe state container for agent communication."""
    message: str
    status: str
    feedback: str
    thought_process: str  # Track the agent's reasoning
    session_id: str  # Track the conversation session
    transitions: List[str] = None  # Track state transitions for debugging

    def __post_init__(self):
        if self.transitions is None:
            self.transitions = []
    
    def get(self, key: str, default: Any = None) -> Any:
        """Dictionary-like get method for backward compatibility."""
        return getattr(self, key, default)
    
    def update(self, updates: Dict[str, Any]) -> None:
        """Dictionary-like update method."""
        for key, value in updates.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "message": self.message,
            "status": self.status,
            "feedback": self.feedback,
            "thought_process": self.thought_process,
            "session_id": self.session_id,
            "transitions": self.transitions or []
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentState':
        """Create AgentState from dictionary."""
        return cls(
            message=data.get("message", ""),
            status=data.get("status", "pending"),
            feedback=data.get("feedback", ""),
            thought_process=data.get("thought_process", ""),
            session_id=data.get("session_id", ""),
            transitions=data.get("transitions", [])
        )

class PipelineGraph:
    """Manages the agent workflow graph with enhanced error handling and monitoring."""
    
    def __init__(
        self,
        conversation_manager: Optional[ConversationManager] = None,
        model_name: str = "mistral",
        temperature: float = 0.7
    ):
        self.conversation_manager = conversation_manager
        self.model_name = model_name
        self.temperature = temperature
        self.graph = None
        self._initialize_graph()

    def _initialize_graph(self) -> None:
        """Initialize the agent workflow graph with error handling."""
        try:
            # Try to initialize the language model with Ollama, fallback to mock if not available
            try:
                llm = ChatOpenAI(
                    model=self.model_name,
                    api_key="not-needed",
                    base_url="http://localhost:11434/v1",
                    temperature=self.temperature
                )
                # Test the connection
                test_response = llm.invoke("test")
                logger.info("Successfully connected to Ollama")
            except Exception as ollama_error:
                logger.warning(f"Ollama not available: {ollama_error}. Using mock LLM for testing.")
                # Create a simple mock LLM for testing
                from .mock_llm import MockLLM
                llm = MockLLM()
            
            # Initialize agents with the language model and conversation manager
            self.ceo = CEOAgent(llm=llm, agent_registry=AGENT_REGISTRY, conversation_manager=self.conversation_manager)
            self.worker = WorkerAgent(llm=llm, conversation_manager=self.conversation_manager)
            self.qa = QAAgent(llm=llm, conversation_manager=self.conversation_manager)
            self.reflection = ReflectionAgent(llm=llm, conversation_manager=self.conversation_manager)
            
            # Create agent map for routing
            self.agent_map = {
                "worker": self.worker.run,
                "qa": self.qa.run,
                "reflection": self.reflection.run
            }
            
            # Create the graph
            self.graph = StateGraph(AgentState)
            
            # Add nodes with wrapper functions to handle state conversion
            self.graph.add_node("CEO", self._wrap_agent_function(self.ceo.run))
            for name, fn in self.agent_map.items():
                self.graph.add_node(name.capitalize(), self._wrap_agent_function(fn))
            self.graph.add_node("END", lambda state: state)
            
            # Set entry point
            self.graph.set_entry_point("CEO")
            
            # Add edges with enhanced routing
            self.graph.add_conditional_edges(
                "CEO", 
                self._ceo_router, 
                {**{k.capitalize(): k.capitalize() for k in self.agent_map}, "Reflection": "Reflection", "END": "END"}
            )
            
            # Add edges for agent workflow
            for agent in self.agent_map:
                self.graph.add_edge(agent.capitalize(), "Reflection")
            self.graph.add_edge("Reflection", "CEO")
            
        except Exception as e:
            logger.error(f"Error initializing pipeline graph: {str(e)}")
            raise

    def _wrap_agent_function(self, agent_func: Callable) -> Callable:
        """Wrap agent functions to handle state conversion between AgentState and dict."""
        def wrapper(state: AgentState) -> AgentState:
            try:
                # Convert AgentState to dict for the agent
                state_dict = state.to_dict()
                
                # Call the agent function
                result_dict = agent_func(state_dict)
                
                # Convert result back to AgentState
                result_state = AgentState.from_dict(result_dict)
                
                return result_state
                
            except Exception as e:
                logger.error(f"Error in agent wrapper: {str(e)}")
                # Return error state
                error_state = AgentState(
                    message=state.message,
                    status="error",
                    feedback=f"Agent encountered an error: {str(e)}",
                    thought_process="Error occurred during agent processing",
                    session_id=state.session_id,
                    transitions=state.transitions or []
                )
                return error_state
        
        return wrapper

    def _ceo_router(self, state: AgentState) -> str:
        """
        Enhanced natural language intent detection for CEO routing.
        Uses both thought process and feedback for robust decision making.
        """
        thought = state.thought_process.lower()
        feedback = state.feedback.lower()
        
        # Extract decision from thought process
        if "decide:" in thought:
            decision = thought.split("decide:")[-1].strip()
            decision = decision.split("\n")[0].strip()  # Get first line after DECIDE:
            
            # Check for END decision
            if "end" in decision:
                return "END"
            
            # Check for specific agent decisions
            for agent in self.agent_map:
                if agent in decision:
                    return agent.capitalize()
            
            # If no clear decision, default to reflection
            return "Reflection"
        
        # Fallback to feedback analysis
        completion_phrases = [
            "final answer", "here is my answer", "task is complete",
            "this concludes", "approved", "the outcome is", "the result is",
            "the plan is complete", "proceed with implementation",
            "i have completed", "i have finished", "this is my final",
            "the answer is", "in summary", "to summarize", "in conclusion"
        ]
        
        if any(phrase in feedback for phrase in completion_phrases):
            return "END"
        
        # Route to agent if CEO mentions them
        for agent in self.agent_map:
            if agent in feedback:
                return agent.capitalize()
        
        # Route to reflection if CEO asks to reflect or review
        reflection_phrases = [
            "reflect", "reflection", "let's review", "let me review",
            "self-reflect", "self reflection", "let's think", "let's consider"
        ]
        
        if any(phrase in feedback for phrase in reflection_phrases):
            return "Reflection"
        
        # Default: reflect for continuous improvement
        return "Reflection"

    def run(self, initial_state: AgentState) -> AgentState:
        """
        Execute the agent workflow with the given initial state.
        Includes progress tracking and error handling.
        """
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Running agent workflow...", total=None)
                
                # Compile and run the graph
                compiled_graph = self.graph.compile()
                result = compiled_graph.invoke(initial_state)
                
                progress.update(task, completed=True)
                return result
                
        except Exception as e:
            logger.error(f"Error executing agent workflow: {str(e)}")
            raise

def create_agent_graph(conversation_manager: Optional[ConversationManager] = None) -> PipelineGraph:
    """
    Factory function to create and initialize the agent pipeline graph.
    
    Args:
        conversation_manager: Optional conversation manager for tracking chat history
        
    Returns:
        PipelineGraph: Initialized pipeline graph instance
    """
    return PipelineGraph(conversation_manager=conversation_manager)

def print_mermaid():
    """Print the workflow diagram using Mermaid syntax."""
    console.print(Panel.fit('''
flowchart TD
    CEO_START((CEO_START)) --> Worker((Worker))
    Worker --> QA((QA))
    QA --> CEO_REVIEW((CEO_REVIEW))
    CEO_REVIEW -- done --> END((END))
    CEO_REVIEW -- needs_revision --> Worker
    CEO_START -- reflect --> Reflection((Reflection))
    Reflection --> CEO_START
''', title="Agent Pipeline Workflow"))

def process_task(graph, state: AgentState) -> Dict[str, Any]:
    """Process a single task through the agent pipeline."""
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Processing task...", total=None)
            
            # Execute the graph
            result = graph.invoke(state)
            
            progress.update(task, completed=True)
            return result
    except Exception as e:
        logger.error(f"Error processing task: {str(e)}")
        return {
            "message": state["message"],
            "status": "error",
            "feedback": f"Error processing task: {str(e)}",
            "thought_process": "Error occurred during processing"
        }

def main():
    """Main function to run the agent graph."""
    try:
        console.print("\n[bold blue]=== AI-Lab Agent Pipeline ===[/bold blue]\n")
        
        # Create and compile the graph
        graph = create_agent_graph()
        compiled_graph = graph.compile()
        
        # Print workflow diagram
        print_mermaid()
        
        console.print("\n[bold green]Enter a question (or 'quit' to exit):[/bold green]")
        
        while True:
            question = console.input("[bold yellow]>[/bold yellow] ").strip()
            
            if question.lower() == "quit":
                break
                
            console.print("\n[bold]Processing...[/bold]")
            
            # Initialize state with thought process tracking
            state = AgentState(
                message=question,
                status="pending",
                feedback="",
                thought_process=""
            )
            
            # Process the task
            result = process_task(compiled_graph, state)
            
            # Display results with thought process
            console.print("\n[bold]Results:[/bold]")
            console.print(Panel(
                f"[bold]Status:[/bold] {result['status']}\n\n[bold]Thought Process:[/bold]\n{result.get('thought_process', 'No thought process recorded')}\n\n[bold]Feedback:[/bold]\n{result['feedback']}",
                title="Task Results",
                border_style="green" if result['status'] == "done" else "red"
            ))
            
            console.print()  # Add spacing
            
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        console.print(f"\n[bold red]Error:[/bold red] {str(e)}")

if __name__ == "__main__":
    main() 