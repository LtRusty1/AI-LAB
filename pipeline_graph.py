"""
Pipeline graph implementation for the root-level Streamlit app.
"""

from typing import Dict, Any, TypedDict, Annotated, List, Tuple
from langgraph.graph import StateGraph
from langchain_openai import ChatOpenAI
from agents import CEOAgent, WorkerAgent, QAAgent, AgentState
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_agent_graph() -> StateGraph:
    """
    Creates and configures the agent workflow graph.
    """
    try:
        # Initialize the language model
        llm = ChatOpenAI(
            model="mistral",
            api_key="not-needed",
            base_url="http://localhost:11434/v1",
            temperature=0.7
        )
        
        # Initialize agents
        ceo = CEOAgent(llm=llm)
        worker = WorkerAgent(llm=llm)
        qa = QAAgent(llm=llm)
        
        # Create the graph
        graph = StateGraph(AgentState)
        
        # Add nodes
        graph.add_node("CEO_START", ceo.run)
        graph.add_node("Worker", worker.run)
        graph.add_node("QA", qa.run)
        graph.add_node("CEO_REVIEW", ceo.run)
        graph.add_node("END", lambda state: state)
        
        # Set entry point
        graph.set_entry_point("CEO_START")
        
        # CEO routing logic
        def ceo_router(state):
            status = state.get("status", "")
            if status == "done":
                return "END"
            elif status == "needs_help":
                return "Worker"
            else:
                return "END"
        
        def ceo_review_router(state):
            feedback = state.get("feedback", "").lower()
            if "done" in feedback or "approved" in feedback or "complete" in feedback:
                return "END"
            else:
                return "Worker"
        
        # Add conditional edges
        graph.add_conditional_edges(
            "CEO_START", 
            ceo_router, 
            {"Worker": "Worker", "END": "END"}
        )
        
        graph.add_edge("Worker", "QA")
        graph.add_edge("QA", "CEO_REVIEW")
        
        graph.add_conditional_edges(
            "CEO_REVIEW",
            ceo_review_router,
            {"Worker": "Worker", "END": "END"}
        )
        
        return graph
        
    except Exception as e:
        logger.error(f"Error creating agent graph: {str(e)}")
        raise

if __name__ == "__main__":
    # Test the graph creation
    graph = create_agent_graph()
    compiled_graph = graph.compile()
    
    # Test with a simple state
    test_state = AgentState(
        message="Hello, can you help me?",
        status="pending",
        feedback="",
        transitions=[]
    )
    
    result = compiled_graph.invoke(test_state)
    print(f"Test result: {result}") 