"""
CEO Agent implementation.
"""

from typing import Dict, Any, Optional
from langchain.agents import AgentExecutor
from langchain.prompts import ChatPromptTemplate
from langchain.tools import Tool
import time
import logging

logger = logging.getLogger(__name__)

class CEOAgent:
    def __init__(self, llm, agent_registry, conversation_manager=None):
        self.llm = llm
        self.agent_registry = agent_registry
        self.conversation_manager = conversation_manager
        self.max_retries = 3
        self.retry_delay = 1  # seconds
        
        # Define the CEO's prompt template with few-shot examples
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are the CEO of an AI organization. Your role is to:
1. ANALYZE incoming requests and understand their requirements
2. PLAN the best approach to handle the request
3. DECIDE which agent(s) should handle the task
4. EXPLAIN your reasoning and decisions

You MUST follow this structured thinking process:
ANALYZE: What is the request asking for? What are the key requirements?
PLAN: What steps are needed to fulfill this request?
DECIDE: Which agent(s) should handle this task and why? You MUST choose one of: Worker, QA, Reflection, or END
EXPLAIN: Document your reasoning and decisions

You MUST provide your thought process in this EXACT format:
ANALYZE: [Your analysis]
PLAN: [Your plan]
DECIDE: [Your decision - MUST be one of: Worker, QA, Reflection, or END]
EXPLAIN: [Your explanation]

Make autonomous decisions based on your analysis. You have access to these agents:
- Worker: For implementation and execution tasks
- QA: For quality assurance and review
- Reflection: For self-reflection and improvement
- END: When the task is complete and no further action is needed

Your decision MUST be clear and actionable. You MUST choose one of the available options.

Here are some examples of good responses:

Example 1:
Human: What is the next step to implement?
ANALYZE: The user is asking for guidance on implementation steps. This requires a detailed plan and execution strategy.
PLAN: 1. Break down the implementation into clear steps
2. Identify required components
3. Create a timeline
4. Assign resources
DECIDE: Worker
EXPLAIN: This task requires implementation planning and execution, which is the Worker's expertise. The Worker can create a detailed implementation plan and begin execution.

Example 2:
Human: Can you review the current implementation?
ANALYZE: The user wants a quality review of the current implementation. This requires careful analysis and validation.
PLAN: 1. Review the implementation details
2. Check for best practices
3. Identify potential issues
4. Provide feedback
DECIDE: QA
EXPLAIN: This is a quality assurance task that requires thorough review and validation. The QA agent is best suited for this task.

Example 3:
Human: Let's think about how we can improve our process
ANALYZE: The user wants to reflect on and improve the current process. This requires deep analysis and strategic thinking.
PLAN: 1. Review current process
2. Identify areas for improvement
3. Suggest enhancements
4. Create improvement plan
DECIDE: Reflection
EXPLAIN: This task requires deep reflection and strategic thinking about process improvement. The Reflection agent is best suited for this task."""),
            ("human", "{context}\n\nCurrent request: {message}")
        ])
        
        # Create the agent executor with the prompt
        self.agent = AgentExecutor.from_agent_and_tools(
            agent=self.llm,
            tools=[],
            verbose=True,
            handle_parsing_errors=True
        )
    
    def _validate_response(self, output: str) -> bool:
        """Validate that the response contains all required sections."""
        required_sections = ["ANALYZE:", "PLAN:", "DECIDE:", "EXPLAIN:"]
        return all(section in output for section in required_sections)
    
    def _extract_thought_process(self, output: str) -> str:
        """Extract thought process from the response."""
        thought_process = ""
        sections = ["ANALYZE:", "PLAN:", "DECIDE:", "EXPLAIN:"]
        for section in sections:
            if section in output:
                start = output.find(section)
                end = output.find("\n\n", start) if "\n\n" in output[start:] else len(output)
                thought_process += output[start:end].strip() + "\n\n"
        return thought_process.strip()
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Run the CEO agent on the given state."""
        try:
            message = state.get("message", "")
            session_id = state.get("session_id", "")
            context = ""
            if self.conversation_manager and session_id:
                context = self.conversation_manager.get_context(session_id)
            formatted_prompt = self.prompt.format_prompt(message=message, context=context)
            logger.info(f"[CEOAgent] Formatted prompt: {formatted_prompt.to_string()}")
            for attempt in range(self.max_retries):
                try:
                    response = self.agent.invoke(formatted_prompt.to_string())
                    logger.info(f"[CEOAgent] Agent response: {response}")
                    output = response.get("output", "") if isinstance(response, dict) else str(response)
                    if self._validate_response(output):
                        thought_process = self._extract_thought_process(output)
                        if "DECIDE:" not in thought_process:
                            thought_process += "DECIDE: Reflection\n\n"
                            thought_process += "EXPLAIN: No clear decision was made, defaulting to reflection for further analysis.\n\n"
                        state["feedback"] = output
                        state["thought_process"] = thought_process
                        state["status"] = "done" if "DECIDE: END" in thought_process else "pending"
                        if self.conversation_manager and session_id:
                            self.conversation_manager.add_message(
                                session_id,
                                "CEO",
                                output,
                                thought_process
                            )
                        return state
                except Exception as e:
                    logger.error(f"[CEOAgent] Agent invoke error (attempt {attempt+1}): {e}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                    continue
            state["status"] = "error"
            state["feedback"] = "Failed to generate a valid response after multiple attempts."
            state["thought_process"] = "Error: Could not generate a valid response with all required sections."
            return state
        except Exception as e:
            logger.error(f"[CEOAgent] Error in CEO agent: {str(e)}")
            state["status"] = "error"
            state["feedback"] = f"Error in CEO agent: {str(e)}"
            state["thought_process"] = "Error occurred during processing"
            return state 