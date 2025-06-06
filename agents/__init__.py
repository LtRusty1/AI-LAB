"""
Basic agent implementations for the pipeline.
"""

from typing import Any, Dict, Optional, TypedDict, Annotated, List, Tuple
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage
import logging

# Type definition for agent state
class AgentState(TypedDict):
    """Type definition for the state passed between agents."""
    message: Annotated[str, "message"]
    status: Annotated[str, "status"]
    feedback: Annotated[str, "feedback"]
    transitions: Annotated[List[Tuple[str, str]], "transitions"]

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseAgent:
    """Base class for all agents."""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Base run method to be implemented by subclasses."""
        raise NotImplementedError


class CEOAgent(BaseAgent):
    """CEO agent that makes strategic decisions and dynamic routing in natural language."""
    def __init__(self, llm: ChatOpenAI, agent_registry=None):
        super().__init__(llm)
        self.agent_registry = agent_registry or AGENT_REGISTRY

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            available_agents = ', '.join(self.agent_registry.keys())
            if state.get("status") == "pending":
                # Initial request from Chairman
                prompt = ChatPromptTemplate.from_messages([
                    SystemMessage(content=f"""
You are the CEO of a company, and you must think and act autonomously. When responding to the Chairman (user), follow these steps:

1. THINK: First, analyze the request carefully and think through your response step by step.
2. PLAN: Consider what information or help you need to provide a complete answer.
3. DECIDE: Choose whether to:
   - Answer directly if you have all necessary information
   - Delegate to another agent if specialized knowledge is needed
   - Request reflection if the answer needs improvement
4. ACT: Take action based on your decision
5. EXPLAIN: Always explain your thought process and reasoning

When delegating to other agents:
- Clearly state which agent you're delegating to and why
- Specify what you need from them
- Explain how their input will help solve the problem

When providing a final answer:
- Summarize the key points
- Explain your reasoning
- Provide actionable next steps if applicable

Available agents: {available_agents}

Remember: You are an autonomous agent. Think step by step, make decisions, and take action. Don't just acknowledge the request - solve it.
"""),
                    HumanMessage(content=f"Chairman request: {state['message']}\n\nThink through your response step by step and explain your reasoning before taking action.")
                ])
                response = self.llm.invoke(prompt.format_messages())
                logger.info("CEO natural language analysis completed")
                return {
                    "message": state["message"],
                    "status": "in_progress",
                    "feedback": response.content
                }
            else:
                # Review feedback or retro-feedback
                feedback = state.get("feedback", "")
                prompt = ChatPromptTemplate.from_messages([
                    SystemMessage(content=f"""
You are the CEO reviewing feedback from your team. Follow these steps:

1. ANALYZE: Review the feedback carefully
2. EVALUATE: Consider if the feedback is sufficient
3. DECIDE: Choose to:
   - Request more information if needed
   - Ask for reflection if improvements are possible
   - Provide a final answer if complete
4. ACT: Take appropriate action
5. EXPLAIN: Document your reasoning

Available agents: {available_agents}

Remember: You are an autonomous agent. Think step by step, make decisions, and take action. Don't just acknowledge the feedback - use it to move forward.
"""),
                    HumanMessage(content=f"Task: {state['message']}\nFeedback received: {feedback}\n\nThink through your response step by step and explain your reasoning before taking action.")
                ])
                response = self.llm.invoke(prompt.format_messages())
                logger.info("CEO review and natural routing completed")
                return {
                    "message": state["message"],
                    "status": "in_progress",
                    "feedback": response.content
                }
        except Exception as e:
            logger.error(f"Error in CEO agent: {str(e)}")
            return {
                "message": state["message"],
                "status": "error",
                "feedback": f"Error in CEO processing: {str(e)}"
            }

class WorkerAgent(BaseAgent):
    """Worker agent that performs the main task."""
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process the task and generate output."""
        try:
            prompt = ChatPromptTemplate.from_messages([
                SystemMessage(content="""You are a Worker agent responsible for executing tasks. You must think and act autonomously. Follow these steps:

1. ANALYZE: Understand the task requirements thoroughly
2. PLAN: Break down the task into steps and consider potential challenges
3. EXECUTE: Implement the solution step by step
4. VERIFY: Check your work for completeness and quality
5. EXPLAIN: Document your process and reasoning

When implementing solutions:
- Think through each step carefully
- Consider edge cases and potential issues
- Provide clear, well-structured responses
- Include explanations for your decisions
- Suggest improvements or alternatives when relevant

Remember: You are an autonomous agent. Don't just complete the task - think through it, make decisions, and explain your reasoning.
"""),
                HumanMessage(content=f"Task to complete: {state['message']}\n\nThink through your solution step by step and explain your reasoning before providing the final answer.")
            ])
            
            response = self.llm.invoke(prompt.format_messages())
            logger.info("Worker task completed")
            
            return {
                "message": state["message"],
                "status": "in_progress",
                "feedback": response.content
            }
        except Exception as e:
            logger.error(f"Error in Worker agent: {str(e)}")
            return {
                "message": state["message"],
                "status": "error",
                "feedback": f"Error in Worker processing: {str(e)}"
            }

class QAAgent(BaseAgent):
    """QA agent that reviews the work."""
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Review the work and provide feedback."""
        try:
            prompt = ChatPromptTemplate.from_messages([
                SystemMessage(content="""You are a QA agent responsible for reviewing work. You must think and act autonomously. Follow these steps:

1. ANALYZE: Thoroughly examine the work and requirements
2. EVALUATE: Assess quality, accuracy, and completeness
3. IDENTIFY: Find potential issues, improvements, or gaps
4. DECIDE: Determine if the work meets standards
5. EXPLAIN: Provide detailed feedback with reasoning

When reviewing:
- Consider all aspects: functionality, efficiency, readability
- Look for potential issues or edge cases
- Evaluate against best practices
- Provide specific, actionable feedback
- Explain your reasoning for each point

Remember: You are an autonomous agent. Don't just review - think critically, make decisions, and provide detailed, constructive feedback.
"""),
                HumanMessage(content=f"Task: {state['message']}\nWork to review: {state.get('feedback', '')}\n\nThink through your review step by step and explain your reasoning before providing feedback.")
            ])
            
            response = self.llm.invoke(prompt.format_messages())
            logger.info("QA review completed")
            
            return {
                "message": state["message"],
                "status": "in_progress",
                "feedback": response.content
            }
        except Exception as e:
            logger.error(f"Error in QA agent: {str(e)}")
            return {
                "message": state["message"],
                "status": "error",
                "feedback": f"Error in QA processing: {str(e)}"
            }

class ReflectionAgent(BaseAgent):
    """Agent that reviews the latest output and suggests improvements or further actions."""
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            prompt = ChatPromptTemplate.from_messages([
                SystemMessage(content="""
You are a Reflection agent responsible for improving work quality. You must think and act autonomously. Follow these steps:

1. ANALYZE: Review the current output and context
2. EVALUATE: Assess the quality and completeness
3. IDENTIFY: Find areas for improvement
4. SUGGEST: Propose specific enhancements
5. EXPLAIN: Document your reasoning

When reflecting:
- Consider multiple perspectives
- Look for potential improvements
- Evaluate against goals and requirements
- Provide specific, actionable suggestions
- Explain your reasoning for each point

Remember: You are an autonomous agent. Don't just review - think deeply, identify opportunities for improvement, and provide detailed, constructive suggestions.
"""),
                HumanMessage(content=f"Task: {state['message']}\nLatest output: {state.get('feedback', '')}\n\nThink through your reflection step by step and explain your reasoning before providing suggestions.")
            ])
            response = self.llm.invoke(prompt.format_messages())
            logger.info("Reflection completed")
            return {
                "message": state["message"],
                "status": "in_progress",
                "feedback": response.content
            }
        except Exception as e:
            logger.error(f"Error in Reflection agent: {str(e)}")
            return {
                "message": state["message"],
                "status": "error",
                "feedback": f"Error in Reflection processing: {str(e)}"
            }

# Registry of available agents. Defined after all agent classes to
# avoid NameError during module import.
AGENT_REGISTRY = {
    "worker": WorkerAgent,
    "qa": QAAgent,
    # Add more agents here as needed
}

# Export the classes for easy importing
__all__ = ['AgentState', 'BaseAgent', 'CEOAgent', 'WorkerAgent', 'QAAgent', 'ReflectionAgent', 'AGENT_REGISTRY']
