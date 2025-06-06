import streamlit as st
from pipeline_graph import create_agent_graph, AgentState
import time
from visualization import AgentVisualizer
import threading

# Configure Streamlit page
st.set_page_config(
    page_title="AI-Lab Agent Pipeline",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'graph' not in st.session_state:
    st.session_state.graph = create_agent_graph().compile()
if 'visualizer' not in st.session_state:
    st.session_state.visualizer = AgentVisualizer()
if 'animation_running' not in st.session_state:
    st.session_state.animation_running = False
if 'current_frame' not in st.session_state:
    st.session_state.current_frame = 0
if 'llm_result' not in st.session_state:
    st.session_state.llm_result = None
if 'llm_processing' not in st.session_state:
    st.session_state.llm_processing = False
if 'llm_thread' not in st.session_state:
    st.session_state.llm_thread = None
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'last_transitions' not in st.session_state:
    st.session_state.last_transitions = []
if 'llm_thread_result' not in st.session_state:
    st.session_state.llm_thread_result = None

st.title("🤖 AI-Lab Agent Pipeline")

# Create two columns
col1, col2 = st.columns([2, 1])

# Sidebar for settings
with st.sidebar:
    st.header("Settings")
    st.info("The CEO agent will handle your queries directly when possible, and involve other agents only when needed.")
    
    # Animation controls
    st.header("Animation Controls")
    if st.button("Reset Animation"):
        st.session_state.animation_running = False
        st.session_state.visualizer = AgentVisualizer()
        st.session_state.current_frame = 0
        st.session_state.llm_result = None
        st.session_state.llm_processing = False
        st.session_state.llm_thread = None
        st.session_state.last_transitions = []
        st.session_state.llm_thread_result = None

# Main chat interface in the right column
with col2:
    st.markdown("""
    ### Chat Interface
    Type your message below and press Enter to start a conversation with the AI agents.
    """)

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    prompt = st.chat_input("What would you like to know?")
    if prompt and not st.session_state.llm_processing:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Prepare for LLM processing
        st.session_state.llm_result = None
        st.session_state.llm_processing = True
        st.session_state.last_transitions = []
        st.session_state.llm_thread_result = None

        # Start LLM processing in a background thread
        def llm_task(graph, prompt):
            state = AgentState(
                message=prompt,
                status="pending",
                feedback="",
                transitions=[]  # Initialize transitions as empty list
            )
            result = graph.invoke(state)
            # Only return the result, do not touch st.session_state
            return {"feedback": result["feedback"], "transitions": result.get("transitions", [])}

        def thread_wrapper(graph, prompt):
            result = llm_task(graph, prompt)
            st.session_state.llm_thread_result = result
            st.session_state.llm_processing = False

        thread = threading.Thread(target=thread_wrapper, args=(st.session_state.graph, prompt))
        thread.start()
        st.session_state.llm_thread = thread

    # Check if thread has finished and update session state
    if st.session_state.llm_thread_result is not None:
        st.session_state.llm_result = st.session_state.llm_thread_result["feedback"]
        st.session_state.last_transitions = st.session_state.llm_thread_result["transitions"]
        st.session_state.llm_thread_result = None
        # Animate the real path after LLM finishes
        if st.session_state.last_transitions:
            flow_sequence = [[edge] for edge in st.session_state.last_transitions]
            st.session_state.visualizer.animate_flow(flow_sequence)
            st.session_state.animation_running = True
            st.session_state.current_frame = 0
            st.session_state.last_transitions = []  # Clear to avoid re-triggering
            st.experimental_rerun()

    # Show LLM result if available
    if st.session_state.llm_result:
        with st.chat_message("assistant"):
            st.markdown(st.session_state.llm_result)
        # Add assistant response to chat history if not already present
        if not st.session_state.messages or st.session_state.messages[-1].get("role") != "assistant":
            st.session_state.messages.append({"role": "assistant", "content": st.session_state.llm_result})

# Agent Pipeline Visualization in the left column
with col1:
    st.markdown("""
    ### Agent Pipeline Visualization
    Watch how information flows between agents in real-time.
    """)
    
    animation_placeholder = st.empty()
    
    # Real-time animation while LLM is processing or after
    if st.session_state.animation_running:
        frame = st.session_state.visualizer.animation_frames[st.session_state.current_frame]
        animation_placeholder.plotly_chart(frame, use_container_width=True, config={'displayModeBar': False})
        st.session_state.current_frame = (st.session_state.current_frame + 1) % len(st.session_state.visualizer.animation_frames)
        time.sleep(0.1)
        st.experimental_rerun()
    
    # --- DEBUG: Show static org chart ---
    st.markdown("#### Static Organization Chart (Debug)")
    static_fig = st.session_state.visualizer.create_animation_frame([])
    st.plotly_chart(static_fig, use_container_width=True) 