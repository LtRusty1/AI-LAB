"""
Pipeline graph implementation using LangGraph to orchestrate CEO, QA, and Worker agents.
"""

from typing import Dict, Any, TypedDict, Annotated
from langgraph.graph import StateGraph
from langchain_openai import ChatOpenAI
from agents import CEOAgent, QAAgent, WorkerAgent, ReflectionAgent, AGENT_REGISTRY
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

def create_agent_graph() -> StateGraph:
    """
    Creates and configures the agent workflow graph with dynamic routing and reflection.
    """
    try:
        llm = ChatOpenAI(
            model="mistral",
            api_key="not-needed",
            base_url="http://localhost:11434/v1"
        )
        # Instantiate agents
        ceo = CEOAgent(llm=llm, agent_registry=AGENT_REGISTRY)
        worker = WorkerAgent(llm=llm)
        qa = QAAgent(llm=llm)
        reflection = ReflectionAgent(llm=llm)
        agent_map = {
            "worker": worker.run,
            "qa": qa.run,
            # Add more agents here as needed
        }
        graph = StateGraph(AgentState)
        graph.add_node("CEO", ceo.run)
        graph.add_node("Reflection", reflection.run)
        for name, fn in agent_map.items():
            graph.add_node(name.capitalize(), fn)
        graph.add_node("END", lambda state: state)
        graph.set_entry_point("CEO")
        
        # Enhanced natural language intent detection for CEO routing
        def ceo_router(state):
            fb = state.get("feedback", "").lower()
            thought = state.get("thought_process", "").lower()
            
            # Extract decision from thought process
            if "decision:" in thought:
                decision = thought.split("decision:")[-1].strip()
                if "final answer" in decision or "complete" in decision:
                    return "END"
                for agent in agent_map:
                    if agent in decision:
                        return agent.capitalize()
                if "reflect" in decision or "review" in decision:
                    return "Reflection"
            
            # Fallback to feedback analysis
            if any(phrase in fb for phrase in ["final answer", "here is my answer", "task is complete", "this concludes", "approved", "the outcome is", "the result is", "the plan is complete", "proceed with implementation", "i have completed", "i have finished", "this is my final", "the answer is", "in summary", "to summarize", "in conclusion"]):
                return "END"
            
            # Route to agent if CEO mentions them
            for agent in agent_map:
                if agent in fb:
                    return agent.capitalize()
            
            # Route to reflection if CEO asks to reflect or review
            if any(word in fb for word in ["reflect", "reflection", "let's review", "let me review", "self-reflect", "self reflection", "let's think", "let's consider"]):
                return "Reflection"
            
            # Default: reflect for continuous improvement
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