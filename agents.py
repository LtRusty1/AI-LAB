from typing import Dict, Any, TypedDict, Annotated, List, Tuple
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import logging

logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    """Type definition for the state passed between agents."""
    message: Annotated[str, "message"]
    status: Annotated[str, "status"]
    feedback: Annotated[str, "feedback"]
    transitions: Annotated[List[Tuple[str, str]], "transitions"]

class BaseAgent:
    """Base class for all agents."""
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

class CEOAgent(BaseAgent):
    """CEO agent that coordinates the workflow and makes high-level decisions."""
    
    def __init__(self, llm: ChatOpenAI):
        super().__init__(llm)
        self.organization_structure = {
            "CEO": {
                "role": "Chief Executive Officer",
                "responsibilities": [
                    "Strategic decision making",
                    "Workflow coordination",
                    "Resource allocation",
                    "Quality assurance oversight"
                ],
                "subordinates": ["Worker", "QA"]
            },
            "Worker": {
                "role": "Development Worker",
                "responsibilities": [
                    "Code implementation",
                    "Task execution",
                    "Technical problem solving"
                ]
            },
            "QA": {
                "role": "Quality Assurance",
                "responsibilities": [
                    "Code review",
                    "Quality checks",
                    "Testing"
                ]
            }
        }
        
        # Create the system prompt for the CEO
        self.system_prompt = f"""You are the CEO of an AI development organization. You have the following organization structure:

{self._format_organization_for_prompt()}

Your role is to:
1. Understand and explain the organization structure
2. Make strategic decisions
3. Coordinate between different agents
4. Delegate tasks appropriately
5. Ensure quality of work

Always maintain awareness of your role as CEO and the organization's structure. When asked about the organization, provide detailed information about the roles, responsibilities, and workflow.
"""
        
    def _format_organization_for_prompt(self) -> str:
        """Format the organization structure for the prompt."""
        structure = "Organization Structure:\n\n"
        for role, details in self.organization_structure.items():
            structure += f"{role} ({details['role']}):\n"
            structure += "Responsibilities:\n"
            for resp in details["responsibilities"]:
                structure += f"- {resp}\n"
            if "subordinates" in details:
                structure += f"Manages: {', '.join(details['subordinates'])}\n"
            structure += "\n"
        return structure
        
    def run(self, state: AgentState) -> AgentState:
        """Process the task and decide next steps."""
        try:
            # Create the prompt template
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.system_prompt),
                ("human", "{message}")
            ])
            
            # Format the prompt with the current message
            formatted_prompt = prompt.format_messages(message=state["message"])
            
            # Get response from LLM
            response = self.llm.invoke(formatted_prompt)
            
            transitions = state.get("transitions", [])
            # Determine if we need to delegate
            if "delegate" in response.content.lower() or "worker" in response.content.lower():
                transitions = transitions + [("CEO_START", "Worker")]
                return AgentState(
                    message=state["message"],
                    status="needs_help",
                    feedback="Delegating to Worker for implementation.",
                    transitions=transitions
                )
            # If CEO handles directly
            transitions = transitions + [("CEO_START", "END")]
            return AgentState(
                message=state["message"],
                status="done",
                feedback=response.content,
                transitions=transitions
            )
            
        except Exception as e:
            logger.error(f"Error in CEO agent: {str(e)}")
            return AgentState(
                message=state["message"],
                status="error",
                feedback=f"Error processing request: {str(e)}",
                transitions=state.get("transitions", [])
            )

class WorkerAgent(BaseAgent):
    """Worker agent that handles implementation tasks."""
    
    def run(self, state: AgentState) -> AgentState:
        """Process the task and implement solutions."""
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a Development Worker in an AI organization. Your responsibilities include:\n- Code implementation\n- Task execution\n- Technical problem solving\n\nYou report to the CEO and work closely with the QA team."""),
                ("human", "{message}")
            ])
            formatted_prompt = prompt.format_messages(message=state["message"])
            response = self.llm.invoke(formatted_prompt)
            transitions = state.get("transitions", []) + [("Worker", "QA")]
            return AgentState(
                message=state["message"],
                status="pending",
                feedback=response.content,
                transitions=transitions
            )
        except Exception as e:
            logger.error(f"Error in Worker agent: {str(e)}")
            return AgentState(
                message=state["message"],
                status="error",
                feedback=f"Error processing task: {str(e)}",
                transitions=state.get("transitions", [])
            )

class QAAgent(BaseAgent):
    """Quality Assurance agent that reviews and validates work."""
    
    def run(self, state: AgentState) -> AgentState:
        """Review and validate the work."""
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a Quality Assurance (QA) agent in an AI organization. Your primary role is to ensure the quality and reliability of all work produced.\n\nYour responsibilities include:\n- Code Review: Examining code for quality, best practices, and potential issues\n- Quality Checks: Verifying that work meets required standards and specifications\n- Testing: Ensuring implemented solutions work as expected and are bug-free\n- Documentation Review: Checking that code is well-documented and maintainable\n- Performance Analysis: Evaluating the efficiency and performance of solutions\n\nYou report directly to the CEO and work closely with the Worker team. Your role is crucial in maintaining high standards and preventing issues before they reach production."""),
                ("human", "{message}")
            ])
            formatted_prompt = prompt.format_messages(message=state["message"])
            response = self.llm.invoke(formatted_prompt)
            transitions = state.get("transitions", []) + [("QA", "CEO_REVIEW")]
            return AgentState(
                message=state["message"],
                status="pending",
                feedback=response.content,
                transitions=transitions
            )
        except Exception as e:
            logger.error(f"Error in QA agent: {str(e)}")
            return AgentState(
                message=state["message"],
                status="error",
                feedback=f"Error reviewing work: {str(e)}",
                transitions=state.get("transitions", [])
            ) 