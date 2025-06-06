import streamlit as st
from pipeline_graph import create_agent_graph, AgentState
import time
from visualization import AgentVisualizer

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
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'last_transitions' not in st.session_state:
    st.session_state.last_transitions = []

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
        st.session_state.messages = []
        st.session_state.last_transitions = []

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
    if prompt:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Process LLM request synchronously with loading indicator
        with st.chat_message("assistant"):
            with st.spinner("Processing your request..."):
                # Create agent state
                state = AgentState(
                    message=prompt,
                    status="pending",
                    feedback="",
                    transitions=[]
                )
                
                # Process through the agent pipeline
                result = st.session_state.graph.invoke(state)
                
                # Extract results
                feedback = result.get("feedback", "I apologize, but I couldn't process your request.")
                transitions = result.get("transitions", [])
                
                # Display the response
                st.markdown(feedback)
                
                # Store transitions for animation
                st.session_state.last_transitions = transitions
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": feedback})
                
                # Trigger animation if there are transitions
                if transitions:
                    flow_sequence = [[edge] for edge in transitions]
                    st.session_state.visualizer.animate_flow(flow_sequence)
                    st.session_state.animation_running = True
                    st.session_state.current_frame = 0
                    st.rerun()

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
        st.rerun()
    
    # --- DEBUG: Show static org chart ---
    st.markdown("#### Static Organization Chart (Debug)")
    static_fig = st.session_state.visualizer.create_animation_frame([])
    st.plotly_chart(static_fig, use_container_width=True) 