# Ollama Installation and Setup Guide

## Progress and Accomplishments
1. Initial Setup (May 27, 2025):
   - Successfully located Ollama installation in AppData directory
   - Verified GPU support (NVIDIA RTX 2070 SUPER)
   - Confirmed CUDA integration (v12.9)

2. Service Configuration:
   - Identified correct paths for executables
   - Tested both Command Prompt and PowerShell startup methods
   - Verified service runs on port 11434 (default)

3. Multi-Agent Development:
   - Created initial multi-agent example with coder and critic agents
   - Implemented LCS (Longest Common Subsequence) problem as a test case
   - Set up agent interaction framework with GPU acceleration

4. Current Status:
   - Ollama service is installed and configured
   - GPU acceleration is properly set up and tested
   - Ready for model deployment and agent testing

## Installation Location
Ollama is installed in the following location:
```
C:\Users\User\AppData\Local\Programs\Ollama
```

Key files and directories:
- `ollama.exe` - Main Ollama executable
- `ollama app.exe` - GUI application
- `lib/` - Contains necessary DLLs and dependencies
  - `ollama/` - Core libraries
  - `cuda_v12/` - CUDA support for GPU acceleration

## System Requirements
- Windows 10/11
- NVIDIA GPU (RTX 2070 SUPER detected in this installation)
- CUDA support (v12.9 detected)

## Starting Ollama
There are two ways to start Ollama:

1. Using Command Prompt (Recommended):
```cmd
cd %LOCALAPPDATA%\Programs\Ollama
ollama.exe serve
```

2. Using PowerShell:
```powershell
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" serve
```

## Pulling Models
To download and use models, open a new Command Prompt window and run:
```cmd
ollama pull mistral  # or any other model name
```

## Verifying Installation
To verify Ollama is running correctly:
1. Check if the service is running:
```cmd
curl http://localhost:11434/api/tags
```

2. Try pulling a model:
```cmd
ollama pull mistral
```

## Troubleshooting
If Ollama fails to start:
1. Ensure no other Ollama processes are running
2. Try running Command Prompt as administrator
3. Check if the CUDA drivers are properly installed
4. Verify the installation path is correct
5. **Port mismatch:**
   - By default, Ollama runs on port `11434`. If your script or client uses a different port, update it to match `11434`.
   - You can specify the port when starting Ollama with `ollama.exe serve --port 11434` if needed.

## Multi-Agent Example
The multi-agent example using Ollama is located in:
```
C:\AI-lab\AutoGen\examples\ollama\multi.py
```

## GPU Configuration
The example is configured to use GPU acceleration with the following settings:
- CUDA v12.9
- NVIDIA GeForce RTX 2070 SUPER
- 8GB VRAM
- Optimized batch size and context window for GPU processing

To modify GPU settings, adjust the following parameters in `multi.py`:
```python
gpu_options = Options(
    num_gpu=1,      # Number of GPUs to use
    num_thread=4,   # CPU threads for non-GPU operations
    num_ctx=4096,   # Context window size
    num_batch=512,  # Batch size for processing
    num_keep=32,    # Number of tokens to keep from input
    temperature=0.7,# Sampling temperature
    top_k=40,       # Top-k sampling
    top_p=0.9       # Top-p sampling
)

client = OllamaChatCompletionClient(
    model="mistral:latest",
    options=gpu_options,
    host="http://localhost:11434"  # Default Ollama port
)
```

## Notes
- The installation uses CUDA for GPU acceleration
- The service runs on port 11434 by default
- Models are stored locally after being pulled
- The GUI application can be used for easier model management

## Future Reference
- Installation date: May 27, 2025
- GPU: NVIDIA GeForce RTX 2070 SUPER
- CUDA Version: v12.9
- Driver Version: 12.9
- **Tested: Multi-agent example works with GPU acceleration and correct port configuration.**

# AI-Lab Agent Pipeline

## Overview

This project implements a modular, extensible multi-agent pipeline for organizational task automation and decision-making. The system is designed for a "Chairman-to-CEO" workflow, where the user (Chairman) communicates with a CEO agent, who can dynamically delegate tasks to specialized agents (e.g., Worker, QA) and request self-reflection cycles for iterative improvement.

- **Dynamic agent routing:** CEO analyzes requests and delegates to the appropriate agent(s) or answers directly.
- **Reflection:** After each agent's output, a ReflectionAgent reviews and suggests improvements or further actions.
- **Extensible:** Add new agents easily by updating the agent registry.
- **Interactive CLI:** Run the pipeline and interact as the Chairman via the command line.

## Key Files & Structure

- `agents/__init__.py`  
  Contains all agent class definitions:
  - `CEOAgent`: Dynamic routing, decision-making, and final approval.
  - `WorkerAgent`: Task implementation.
  - `QAAgent`: Quality assurance and review.
  - `ReflectionAgent`: Self-reflection and iterative improvement.
  - `AGENT_REGISTRY`: Dictionary mapping agent names to classes for extensibility.

- `pipeline_graph.py`  
  Defines the LangGraph pipeline:
  - Entry point: Chairman (user) → CEO
  - CEO dynamically routes to any agent in the registry
  - After each agent, ReflectionAgent reviews output
  - CEO reviews reflection and decides next step
  - Loop continues until CEO marks the answer as final

## How to Add a New Agent

1. **Define the agent class** in `agents/__init__.py` (subclass `BaseAgent`).
2. **Add the agent to `AGENT_REGISTRY`** with a unique key (e.g., `"designer": DesignerAgent`).
3. The CEO will now be able to delegate to this agent by name in its prompt/decision.

## How the Pipeline Works

1. **Chairman (user) submits a request** via CLI.
2. **CEOAgent** analyzes the request and decides to answer, delegate, or request reflection.
3. **Delegated agent** (e.g., Worker, QA) processes the task.
4. **ReflectionAgent** reviews the output and suggests improvements or next steps.
5. **CEOAgent** reviews the reflection and decides the next action.
6. **Loop** continues until CEO marks the answer as final ("done").

## Sample Interaction

```
> We need to implement a new user authentication system with OAuth2. What should be the next step?

CEO: The Chairman has requested implementation of a new user authentication system with OAuth2. I will delegate the technical planning to the Worker agent.

Worker: To integrate OAuth2 authentication, I propose: ...

Reflection: The Worker provided a clear plan, but should specify security considerations and recommend libraries.

CEO: Worker, please update your plan to include security best practices and recommend specific libraries for OAuth2 integration.

Worker: Updated plan: ...

Reflection: The updated plan now addresses security and technology choices. The plan is comprehensive.

CEO: The plan is now complete and approved. Proceed with implementation as outlined.

Status: done
Feedback: The plan for OAuth2 authentication is complete and approved. Proceed with implementation as outlined.
```

## Main Entry Point
- Run the pipeline with:
  ```
  python pipeline_graph.py
  ```
- Interact as the Chairman via the CLI prompt.

## For Future Reference
- **Agent logic and registry:** `agents/__init__.py`
- **Pipeline wiring and CLI:** `pipeline_graph.py`
- **Add new agents:** Define in `agents/__init__.py` and add to `AGENT_REGISTRY`
- **Reflection and self-improvement:** Handled by `ReflectionAgent` and CEO's dynamic routing

---

For any rebuild or review, start with these two files and follow the extensibility pattern above.

## Architecture
- **CEO_START**: Entry node. Assigns the task to the Worker.
- **Worker**: Performs the main task.
- **QA**: Reviews the work and provides feedback.
- **CEO_REVIEW**: Reviews QA feedback. If the task is complete, ends the workflow; otherwise, sends it back to the Worker for revision.
- **END**: Terminal node.

### Graph Flow (Mermaid)
```
flowchart TD
    CEO_START((CEO_START)) --> Worker((Worker))
    Worker --> QA((QA))
    QA --> CEO_REVIEW((CEO_REVIEW))
    CEO_REVIEW -- done --> END((END))
    CEO_REVIEW -- needs_revision --> Worker
```

## CLI Usage
Run the pipeline with:
```sh
python pipeline_graph.py
```
You will see the Mermaid graph and be prompted to enter a question. The pipeline will process your input through the agents and print the final status and feedback. Type `quit` to exit.

## Agent Implementation
Agents are defined in `agents/__init__.py`:
- `CEOAgent`: Handles both initial assignment and review of QA feedback.
- `WorkerAgent`: Simulates task execution.
- `QAAgent`: Simulates QA review.

## Extending the Pipeline
- **Add new agents**: Define new agent classes and add them as nodes in the graph.
- **Add branches/conditions**: Use `add_conditional_edges` to route tasks based on state.
- **Integrate real LLMs**: Replace the LLM initialization in `pipeline_graph.py` with your preferred model or endpoint (e.g., Ollama, OpenAI, etc.).
- **Parallel/complex flows**: LangGraph supports more advanced topologies as your needs grow.

## Dependencies
- `langgraph`
- `langchain-openai`
- `autogen-agentchat`, `autogen-core`, `autogen-ext`

Install dependencies with:
```sh
pip install -r requirements.txt
```

## Notes
- The pipeline is designed for easy modification and future expansion.
- For troubleshooting LangGraph errors, see: https://python.langchain.com/docs/troubleshooting/
- For more advanced agent logic, update the agent classes in `agents/__init__.py`.

## Technical Reference

### Environment
- **Python version:** 3.10+
- **OS:** Windows 10/11 (tested with WSL2 and native Windows)
- **LLM backend:** Ollama (default), running on `http://localhost:11434` (can be changed in `pipeline_graph.py`)
- **Default model:** `mistral` (can be changed in the LLM instantiation)

### Key Dependencies
- `langgraph`: Orchestrates the agent pipeline as a state graph.
- `langchain-openai`: Provides the `ChatOpenAI` wrapper for LLM calls (compatible with Ollama's OpenAI endpoint).
- `autogen-agentchat`, `autogen-core`, `autogen-ext`: (Optional) For advanced agent and tool integrations.
- `rich`: For CLI output and progress display.

### Agent Instantiation & Registry
- All agent classes are defined in `agents/__init__.py`.
- Agents are instantiated in `pipeline_graph.py` with the shared LLM instance.
- The `AGENT_REGISTRY` dictionary in `agents/__init__.py` maps agent names (lowercase) to their classes. Add new agents here for CEO to delegate to them.

### Dynamic Routing & Reflection
- The CEO agent's prompt instructs it to decide whether to answer, delegate to a specific agent, or request a reflection cycle.
- After any agent acts, the `ReflectionAgent` reviews the output and suggests improvements or next steps.
- The CEO reviews the reflection and decides the next action.
- Routing logic is implemented in the `ceo_router` function in `pipeline_graph.py`.
- The pipeline loops until the CEO's feedback contains a final/approval keyword ("done", "final", etc.).

### Adding/Updating Agents
- **To add a new agent:**
  1. Define a new class in `agents/__init__.py` (subclass `BaseAgent`).
  2. Add it to `AGENT_REGISTRY` with a unique key.
  3. Optionally, add it to the `agent_map` in `pipeline_graph.py` if you want it as a node in the graph.
- **To update pipeline logic:**
  - Edit `pipeline_graph.py` (graph wiring, routing, CLI, LLM config).
  - Edit `agents/__init__.py` (agent logic, registry).

### Configuration & Environment
- **LLM endpoint and model:** Set in `pipeline_graph.py` (see `ChatOpenAI` instantiation).
- **Ollama port:** Default is `11434`. Change in both Ollama startup and `pipeline_graph.py` if needed.
- **No special environment variables** are required unless customizing LLM endpoints.

### Troubleshooting
- If the LLM does not respond or gives generic answers, check:
  - Ollama is running and accessible at the configured port.
  - The model is pulled and available in Ollama.
  - The agent prompts in `agents/__init__.py` are sufficiently instructive.
- For agent routing issues, check the CEO's feedback and the `ceo_router` logic in `pipeline_graph.py`.
- For dependency issues, ensure all packages in `requirements.txt` are installed.

### Where to Find...
- **Sample interaction:** See the 'Sample Interaction' section above.
- **Extensibility instructions:** See 'How to Add a New Agent' and 'For Future Reference' sections above.
- **Pipeline entry point:** `pipeline_graph.py`
- **Agent logic and registry:** `agents/__init__.py`

---

This section is for future maintainers to quickly understand, review, rebuild, or extend the system.

# AI Lab Project

This repository contains a comprehensive AI development environment with multiple components for building and testing AI applications.

## Project Structure

```
.
├── agents/              # Custom AI agent implementations
├── AutoGen/            # Microsoft AutoGen framework integration
├── backend/            # Backend server and API implementations
├── frontend/           # Frontend web interface
├── ollama/             # Ollama model integration
├── app.py              # Main application entry point
├── agents.py           # Agent management and orchestration
├── auto_scaling.py     # Auto-scaling functionality
├── multi.py            # Multi-agent coordination
├── requirements.txt    # Python dependencies
└── start_ai_lab.bat    # Windows startup script
```

## Features

- Multi-agent AI system
- Auto-scaling capabilities
- Web-based frontend interface
- Backend API services
- Integration with various AI models
- Development and testing tools

## Setup Instructions

1. **Prerequisites**
   - Python 3.8 or higher
   - Git LFS (for large file handling)
   - Windows 10/11 (for .bat scripts)

2. **Installation**
   ```bash
   # Clone the repository
   git clone https://github.com/yourusername/ai-lab.git
   cd ai-lab

   # Install Git LFS
   git lfs install

   # Create and activate virtual environment
   python -m venv venv
   .\venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Running the Project**
   - Use `start_ai_lab.bat` to start the complete environment
   - Or run individual components as needed

## Development

- The project uses Git LFS for large files
- All code is tracked in the repository
- Sensitive data should be stored in .env files (not tracked)
- Follow PEP 8 style guide for Python code

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Your chosen license]

## Contact

[Your contact information] 