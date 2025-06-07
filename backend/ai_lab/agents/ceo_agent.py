"""
CEO Agent implementation.
"""

from typing import Dict, Any, Optional
from langchain.prompts import ChatPromptTemplate
import time
import logging

logger = logging.getLogger(__name__)

class CEOAgent:
    def __init__(self, llm, agent_registry, conversation_manager=None):
        self.llm = llm
        self.agent_registry = agent_registry
        self.conversation_manager = conversation_manager
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
        
        # Define the CEO's prompt template with structured thinking
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are the CEO of an AI development organization. 

Organization Structure:
{org_structure}

Your role is to understand requests, make strategic decisions, and coordinate with your team.

When answering questions about the organization, provide comprehensive information about roles, responsibilities, and structure.

For task requests, you should:
1. ANALYZE the request
2. PLAN the approach
3. DECIDE on the next step
4. EXPLAIN your reasoning

Available next steps:
- Worker: For implementation and technical tasks
- QA: For quality assurance and review
- Reflection: For process improvement and strategic thinking
- END: When the task is complete

Provide clear, professional responses that demonstrate strategic thinking and leadership."""),
            ("human", "{context}\n\nRequest: {message}")
        ])
    
    def _format_organization_for_prompt(self) -> str:
        """Format the organization structure for the prompt."""
        structure = []
        for role, details in self.organization_structure.items():
            role_info = f"{role} ({details['role']}):\n"
            role_info += "Responsibilities:\n"
            for resp in details["responsibilities"]:
                role_info += f"- {resp}\n"
            if "subordinates" in details:
                role_info += f"Manages: {', '.join(details['subordinates'])}\n"
            structure.append(role_info)
        return "\n".join(structure)
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Run the CEO agent on the given state."""
        try:
            message = state.get("message", "")
            session_id = state.get("session_id", "")
            
            # Get conversation context if available
            context = ""
            if self.conversation_manager and session_id:
                context = self.conversation_manager.get_context(session_id)
            
            # Format the organization structure
            org_structure = self._format_organization_for_prompt()
            
            # Create the formatted prompt
            formatted_prompt = self.prompt.format_messages(
                org_structure=org_structure,
                context=context,
                message=message
            )
            
            logger.info(f"[CEOAgent] Processing message: {message}")
            
            # Get response from LLM
            response = self.llm.invoke(formatted_prompt)
            
            # Extract the content
            output = response.content if hasattr(response, 'content') else str(response)
            
            # Create thought process
            thought_process = f"""ANALYZE: Processing request about {message}
PLAN: Providing comprehensive response as CEO
DECIDE: END
EXPLAIN: Completed direct response to user inquiry"""
            
            # Determine if task needs delegation
            needs_delegation = any(keyword in message.lower() for keyword in [
                'implement', 'code', 'develop', 'build', 'create', 'write code'
            ])
            
            needs_qa = any(keyword in message.lower() for keyword in [
                'review', 'check', 'test', 'validate', 'quality'
            ])
            
            needs_reflection = any(keyword in message.lower() for keyword in [
                'improve', 'optimize', 'strategy', 'plan', 'think about'
            ])
            
            # Create new state instead of modifying the existing one
            if needs_delegation:
                status = "needs_worker"
                thought_process = f"""ANALYZE: Request requires implementation work
PLAN: Delegate to development team
DECIDE: Worker
EXPLAIN: This task requires technical implementation which is the Worker's expertise"""
            elif needs_qa:
                status = "needs_qa" 
                thought_process = f"""ANALYZE: Request requires quality assurance
PLAN: Route to QA for review
DECIDE: QA
EXPLAIN: This task requires quality assurance which is the QA team's expertise"""
            elif needs_reflection:
                status = "needs_reflection"
                thought_process = f"""ANALYZE: Request requires strategic thinking
PLAN: Engage reflection process
DECIDE: Reflection
EXPLAIN: This task requires strategic analysis and process improvement"""
            else:
                status = "done"
            
            # Add to conversation history
            if self.conversation_manager and session_id:
                self.conversation_manager.add_message(
                    session_id,
                    "CEO",
                    output,
                    thought_process
                )
            
            # Return updated state as dictionary
            result = dict(state)
            result.update({
                "feedback": output,
                "thought_process": thought_process,
                "status": status
            })
            
            logger.info(f"[CEOAgent] Response generated successfully")
            return result
            
        except Exception as e:
            logger.error(f"[CEOAgent] Error in CEO agent: {str(e)}")
            result = dict(state)
            result.update({
                "status": "error",
                "feedback": f"I apologize, but I encountered an error: {str(e)}",
                "thought_process": "Error occurred during processing"
            })
            return result 