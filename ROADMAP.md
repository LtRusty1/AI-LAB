# Roadmap

This document outlines the strategic goals and planned milestones for AI-Lab development.

## 1. Short-Term (Next 3 Months)

- **Performance Profiling:** Benchmark the system to identify bottlenecks in LLM inference and I/O. Ensure GPU support is enabled for Ollama.
- **Backend Refactoring:** Migrate persistent storage from JSON files to a database (e.g. PostgreSQL) for conversations and agent states.
- **API Key Management UI:** Implement a settings page for entering API keys (OpenAI, Claude, etc.) and select local vs remote models. Store keys securely in the backend.
- **File & Image Support:** Add frontend upload components and backend handlers to process PDFs, text documents, and images. Enable agents to include uploaded content in their context.
- **Enhanced Chat Features:** Improve the chat UI (message streaming, markdown code blocks, multiple sessions). Allow saving and exporting conversation history.

## 2. Mid-Term (Next 6–9 Months)

- **Cross-Platform Frontend:** Choose a framework (Flutter or React Native) and develop native applications for Windows, macOS, iOS, and iPadOS. Ensure UI adapts to different form factors.
- **Plugin Architecture:** Abstract LLM integrations into plugins or services. Refactor the agent pipeline so it can route requests to multiple LLM backends (Ollama, OpenAI, Anthropic, etc.).
- **Modular Agent Configuration:** Allow users to configure or extend the agent/CEO pipeline via the UI. Enable dynamic addition/removal of agents and customization of prompts.
- **File & Image Generation:** Integrate libraries or APIs to generate output files (e.g. PDF reports, PNG/JPEG images from charts or diagrams). Present downloadable results in the GUI.
- **Security & Scalability:** Implement rate limiting and cost controls for external API usage. Containerize services (using Docker) for easier scaling and deployment.

## 3. Long-Term (Next 12–18 Months)

- **Autonomous Improvement Loop:** Develop an "auto-refactor" agent that can suggest code or documentation improvements. Integrate with CI so any changes are tested before merge.
- **Continuous Testing:** Expand test coverage (unit and integration) to safely enable autonomous code updates. Use simulations or sandbox environments to validate agent behaviors.
- **Multi-Agent Collaboration:** Enhance the multi-agent framework (LangGraph) to support large-scale workflows. Possibly integrate external tools or knowledge bases to enrich agent reasoning.
- **User Management:** Add authentication, user roles, and session persistence so multiple users can safely use the system concurrently.
- **Cloud Deployment (Optional):** Explore deploying parts of AI-Lab in the cloud (Kubernetes or managed services) for on-demand scalability of LLM resources.

## Technical Recommendations

- Use **TypeScript** throughout the frontend for type safety and maintainability.
- Adopt UI component libraries (Chakra UI, Material-UI) to accelerate development of a polished design.
- Leverage asynchronous and streaming APIs in FastAPI to keep the UI responsive.
- Employ version control branches and code reviews rigorously before merging autonomous changes.

## Anticipated Challenges and Mitigations

- **Resource Constraints:** Local LLMs can be resource-intensive. Mitigate with model selection (smaller or quantized models) and use of CUDA GPUs.
- **Cross-Platform Consistency:** Ensuring the UI works well on desktop and touch devices. Mitigate by designing adaptive layouts and thoroughly testing on target devices.
- **Security of API Keys:** Sensitive keys must not be exposed. Store them encrypted on the server and never send raw keys to the client.
- **Maintaining Stability:** Automated code changes could introduce bugs. Enforce strict testing and manual approval in the PR workflow before deployment.

This roadmap should be reviewed and updated periodically as the project evolves. 