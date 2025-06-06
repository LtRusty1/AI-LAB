"""
Pipeline graph implementation using LangGraph to orchestrate CEO, QA, and Worker agents.
"""

from typing import Dict, Any, TypedDict, Annotated, Optional
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

class AgentState(TypedDict):
    """Type definition for the state passed between agents."""
    message: Annotated[str, "message"]
    status: Annotated[str, "status"]
    feedback: Annotated[str, "feedback"]
    thought_process: Annotated[str, "thought_process"]  # Track the agent's reasoning
    session_id: Annotated[str, "session_id"]  # Track the conversation session

def create_agent_graph(conversation_manager: Optional[ConversationManager] = None) -> StateGraph:
    """
    Creates and configures the agent workflow graph with dynamic routing and reflection.
    """
    try:
        # Initialize the language model
        llm = ChatOpenAI(
            model="mistral",
            api_key="not-needed",
            base_url="http://localhost:11434/v1",
            temperature=0.7  # Add some creativity to responses
        )
        
        # Initialize agents with the language model and conversation manager
        ceo = CEOAgent(llm=llm, agent_registry=AGENT_REGISTRY, conversation_manager=conversation_manager)
        worker = WorkerAgent(llm=llm, conversation_manager=conversation_manager)
        qa = QAAgent(llm=llm, conversation_manager=conversation_manager)
        reflection = ReflectionAgent(llm=llm, conversation_manager=conversation_manager)
        
        # Create agent map for routing
        agent_map = {
            "worker": worker.run,
            "qa": qa.run,
            "reflection": reflection.run
        }
        
        # Create the graph
        graph = StateGraph(AgentState)
        
        # Add nodes
        graph.add_node("CEO", ceo.run)
        for name, fn in agent_map.items():
            graph.add_node(name.capitalize(), fn)
        graph.add_node("END", lambda state: state)
        
        # Set entry point
        graph.set_entry_point("CEO")
        
        # Enhanced natural language intent detection for CEO routing
        def ceo_router(state):
            thought = state.get("thought_process", "").lower()
            
            # Extract decision from thought process
            if "decide:" in thought:
                decision = thought.split("decide:")[-1].strip()
                decision = decision.split("\n")[0].strip()  # Get first line after DECIDE:
                
                # Check for END decision
                if "end" in decision:
                    return "END"
                
                # Check for specific agent decisions
                for agent in agent_map:
                    if agent in decision:
                        return agent.capitalize()
                
                # If no clear decision, default to reflection
                return "Reflection"
            
            # If no decision found in thought process, default to reflection
            return "Reflection"
        
        # Add edges with enhanced routing
        graph.add_conditional_edges(
            "CEO", 
            ceo_router, 
            {**{k.capitalize(): k.capitalize() for k in agent_map}, "Reflection": "Reflection", "END": "END"}
        )
        
        # Add edges for agent workflow
        for agent in agent_map:
            graph.add_edge(agent.capitalize(), "Reflection")
        graph.add_edge("Reflection", "CEO")
        
        return graph
    except Exception as e:
        logger.error(f"Error creating agent graph: {str(e)}")
        raise

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