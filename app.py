import streamlit as st
import random
import time
from datetime import datetime

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = {}
    
if "current_conversation" not in st.session_state:
    conv_id = random.randint(1000, 9999)
    st.session_state.current_conversation = conv_id
    st.session_state.conversation_history[conv_id] = {
        "messages": [],
        "created": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

# Page configuration
st.set_page_config(
    page_title="ChatBot Pro",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    /* Main chat container */
    .stChatFloatingInputContainer {
        border-radius: 20px;
        padding: 20px;
    }
    
    /* User messages */
    [data-testid="stChatMessage"]:has(.st-emotion-cache-4oy321) {
        justify-content: flex-end;
    }
    
    /* Bot messages */
    [data-testid="stChatMessage"]:has(.st-emotion-cache-1c7y2kd) {
        justify-content: flex-start;
    }
    
    /* Message bubbles */
    .stChatMessage {
        padding: 12px 16px;
        border-radius: 18px;
        margin-bottom: 8px;
        max-width: 80%;
    }
    
    /* User bubble */
    .st-emotion-cache-4oy321 {
        background-color: #0f6cbf;
        color: white;
        border-bottom-right-radius: 2px !important;
    }
    
    /* Bot bubble */
    .st-emotion-cache-1c7y2kd {
        background-color: #f0f2f6;
        color: #333;
        border-bottom-left-radius: 2px !important;
    }
    
    /* Timestamps */
    .message-time {
        font-size: 0.7rem;
        opacity: 0.7;
        margin-top: 4px;
    }
    
    /* Conversation history items */
    .conversation-item {
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 8px;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    
    .conversation-item:hover {
        background-color: #f0f2f6;
    }
    
    .conversation-item.active {
        background-color: #e6f0ff;
        border-left: 3px solid #0f6cbf;
    }
    
    /* Profile section */
    .profile-card {
        background: linear-gradient(180deg, #4a00e0, #8e2de2);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Profile section in sidebar
with st.sidebar:
    st.markdown("""
    <div class="profile-card">
        <div style="display:flex; align-items:center; gap:15px; margin-bottom:20px">
            <div style="font-size:40px">👤</div>
            <div>
                <h3>User Profile</h3>
                <p>Premium Member</p>
            </div>
        </div>
        <div style="display:flex; justify-content:space-between">
            <div>
                <small>Conversations</small>
                <p style="font-size:24px; margin:0">{}</p>
            </div>
            <div>
                <small>Active Since</small>
                <p style="font-size:24px; margin:0">2024</p>
            </div>
        </div>
    </div>
    """.format(len(st.session_state.conversation_history)), unsafe_allow_html=True)
    
    # Personality selector
    st.divider()
    st.markdown("### Settings")
    bot_personality = st.selectbox(
        "Bot Personality",
        ["Friendly Assistant", "Professional Advisor", "Technical Expert", "Casual Buddy"],
        key="personality"
    )

# Conversation history section
with st.sidebar:
    st.divider()
    st.markdown("### Conversation History")
    
    # Display conversation history
    for conv_id, conv_data in st.session_state.conversation_history.items():
        is_active = conv_id == st.session_state.current_conversation
        active_class = "active" if is_active else ""
        
        st.markdown(
            f"""
            <div class="conversation-item {active_class}" onclick="setConversation({conv_id})">
                <div><strong>Chat #{conv_id}</strong></div>
                <small>{conv_data['created']}</small>
                <small>{len(conv_data['messages'])} messages</small>
            </div>
            """,
            unsafe_allow_html=True
        )

# JavaScript to handle conversation switching
st.sidebar.markdown(
    """
    <script>
    function setConversation(convId) {
        Streamlit.setComponentValue(convId);
    }
    </script>
    """,
    unsafe_allow_html=True
)

# Handle conversation switching
conv_selector = st.sidebar.empty()
new_conv = conv_selector.number_input(
    "Select Conversation", 
    min_value=1000,
    max_value=9999,
    value=st.session_state.current_conversation,
    key="conv_selector",
    label_visibility="collapsed"
)

if new_conv != st.session_state.current_conversation:
    if new_conv in st.session_state.conversation_history:
        st.session_state.current_conversation = new_conv
        st.session_state.messages = st.session_state.conversation_history[new_conv]["messages"]
        st.rerun()

# New conversation button
if st.sidebar.button("➕ New Conversation", use_container_width=True):
    new_conv_id = random.randint(1000, 9999)
    st.session_state.current_conversation = new_conv_id
    st.session_state.messages = []
    st.session_state.conversation_history[new_conv_id] = {
        "messages": [],
        "created": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    st.rerun()

# Main chat area
st.title(f"ChatBot Pro - {bot_personality}")
st.caption(f"Conversation ID: #{st.session_state.current_conversation}")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🤖"):
        st.markdown(message["content"])
        st.caption(f"{message['time']} • {message['role'].capitalize()}")

# Chat input
if prompt := st.chat_input("Type your message..."):
    # Add user message to history
    timestamp = datetime.now().strftime("%H:%M:%S")
    user_message = {
        "role": "user", 
        "content": prompt, 
        "time": timestamp
    }
    
    st.session_state.messages.append(user_message)
    st.session_state.conversation_history[st.session_state.current_conversation]["messages"].append(user_message)
    
    # Display user message
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
        st.caption(f"{timestamp} • User")

    # Generate bot response (simulated)
    with st.chat_message("assistant", avatar="🤖"):
        response_container = st.empty()
        simulated_response = ""
        
        # Simulated response based on personality
        responses = {
            "Friendly Assistant": [
                "Great question! Let me think about that...",
                "I'm happy to help with that!",
                "That's an interesting point. Here's what I know..."
            ],
            "Professional Advisor": [
                "Based on my analysis, I recommend...",
                "The optimal approach would be...",
                "After reviewing available data, my assessment is..."
            ],
            "Technical Expert": [
                "From a technical perspective...",
                "The underlying mechanism works as follows...",
                "Considering the technical constraints..."
            ],
            "Casual Buddy": [
                "Oh cool! So here's the deal...",
                "I was just thinking about that too!",
                "Haha, interesting! Let me tell you..."
            ]
        }
        
        # Start with a personality-specific intro
        intro = random.choice(responses[bot_personality])
        simulated_response += intro + " "
        
        # Generate core response
        topics = prompt.split()[:5]
        core_response = f"Regarding {', '.join(topics)}... " + " ".join(
            [f"Lorem ipsum dolor sit amet {random.choice(['consectetur', 'adipiscing', 'elit'])}. "
             for _ in range(random.randint(3, 6))]
        )
        
        # Generate conclusion
        conclusions = [
            "Hope that helps!",
            "Let me know if you need more details.",
            "What else can I assist with?",
            "Does that answer your question?"
        ]
        conclusion = random.choice(conclusions)
        
        full_response = intro + " " + core_response + " " + conclusion
        
        # Simulate streaming response
        for chunk in full_response.split():
            simulated_response += chunk + " "
            response_container.markdown(simulated_response + "▌")
            time.sleep(0.08)  # Adjust speed here
        
        # Display final message
        response_container.markdown(simulated_response)
        timestamp = datetime.now().strftime("%H:%M:%S")
        st.caption(f"{timestamp} • Assistant")
        
        # Add to session state
        bot_message = {
            "role": "assistant", 
            "content": simulated_response, 
            "time": timestamp
        }
        st.session_state.messages.append(bot_message)
        st.session_state.conversation_history[st.session_state.current_conversation]["messages"].append(bot_message)
