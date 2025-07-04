import streamlit as st
import google.generativeai as genai
import random
import os
from datetime import datetime

# 👉 Gemini API Configuration
def setup_gemini():
    """Handle Gemini API key setup securely from file"""
    # First try Streamlit secrets (for deployment)
    try:
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
            genai.configure(api_key=api_key)
            return True
    except:
        pass
    
    # Then try local file (for local development)
    try:
        with open("gemini_api_key.txt", "r") as f:
            api_key = f.read().strip()
        
        if api_key.startswith("AI"):
            genai.configure(api_key=api_key)
            return True
        else:
            st.error("Invalid API key format in file")
            return False
    except FileNotFoundError:
        st.error("API key file not found. Please create 'gemini_api_key.txt' with your key.")
        return False
    except Exception as e:
        st.error(f"Error reading API key: {str(e)}")
        return False

# Initialize Gemini API
if not setup_gemini():
    st.stop()

# 👉 Cache model loading for performance
@st.cache_resource
def load_model():
    return genai.GenerativeModel('gemini-1.5-flash')

model = load_model()

# 👉 Streamlit page setup
st.set_page_config(
    page_title="WiseBuddy Chat 🧠", 
    page_icon="🤖", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 👉 CSS Styling (same as before)
st.markdown("""
    <style>
    /* Main chat container */
    .chat-container {
        display: flex;
        flex-direction: column;
        height: calc(100vh - 200px);
        max-width: 800px;
        margin: 0 auto;
        border: 1px solid #e0e0e0;
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        background-color: #fafafa;
    }
    
    /* Chat history area */
    .chat-history {
        flex: 1;
        overflow-y: auto;
        padding: 20px;
        background-color: #ffffff;
        display: flex;
        flex-direction: column;
        gap: 15px;
    }
    
    /* Message bubbles */
    .user-message {
        align-self: flex-end;
        background-color: #e3f2fd;
        border-radius: 18px 18px 0 18px;
        padding: 12px 18px;
        max-width: 80%;
        animation: fadeIn 0.3s;
    }
    
    .bot-message {
        align-self: flex-start;
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 18px 18px 18px 0;
        padding: 12px 18px;
        max-width: 80%;
        animation: fadeIn 0.3s;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Input area */
    .chat-input {
        padding: 15px;
        background-color: #ffffff;
        border-top: 1px solid #e0e0e0;
        display: flex;
        gap: 10px;
    }
    
    /* Typing indicator */
    .typing-indicator {
        display: flex;
        align-items: center;
        padding: 10px 15px;
        background: #f5f5f5;
        border-radius: 20px;
        color: #666;
        font-style: italic;
    }
    
    .typing-dot {
        width: 8px;
        height: 8px;
        background: #666;
        border-radius: 50%;
        margin: 0 2px;
        animation: typing 1.4s infinite;
    }
    
    .typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .typing-dot:nth-child(3) { animation-delay: 0.4s; }
    
    @keyframes typing {
        0%, 60%, 100% { transform: translateY(0); }
        30% { transform: translateY(-5px); }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Timestamps */
    .timestamp {
        font-size: 0.75rem;
        color: #888;
        margin-top: 4px;
        text-align: right;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
        padding: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# 👉 Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [
        {"sender": "WiseBuddy", "message": "Hello! I'm your WiseBuddy. How can I help you today?", "timestamp": datetime.now().strftime("%H:%M")}
    ]

if 'current_category' not in st.session_state:
    st.session_state.current_category = "🌟 Motivation & Positivity"

if 'temperature' not in st.session_state:
    st.session_state.temperature = 0.7

# 👉 Sidebar configuration
with st.sidebar:
    st.title("⚙️ WiseBuddy Settings")
    
    # Category selection
    st.subheader("Advice Style")
    category = st.selectbox("Choose your advice style:", [
        "🌟 Motivation & Positivity",
        "💡 Business & Wealth",
        "❤️ Love & Relationships",
        "🧘 Mindfulness & Peace"
    ], key="category_select")
    
    # Update category if changed
    if category != st.session_state.current_category:
        st.session_state.current_category = category
        st.session_state.chat_history.append({
            "sender": "WiseBuddy", 
            "message": f"Okay, I'll now focus on providing advice about: **{category}**",
            "timestamp": datetime.now().strftime("%H:%M")
        })
    
    # Temperature control
    st.subheader("Response Style")
    st.session_state.temperature = st.slider(
        "Creativity Level", 
        min_value=0.0, 
        max_value=1.0, 
        value=st.session_state.temperature,
        help="Lower = More factual, Higher = More creative"
    )
    
    # Additional features
    st.subheader("Tools")
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.chat_history = [
            {"sender": "WiseBuddy", "message": "Conversation cleared. How can I help you?", "timestamp": datetime.now().strftime("%H:%M")}
        ]
    
    if st.button("📥 Export Chat", use_container_width=True):
        chat_text = "\n\n".join(
            [f"{msg['sender']} ({msg['timestamp']}):\n{msg['message']}" 
             for msg in st.session_state.chat_history]
        )
        st.download_button(
            label="Download Conversation",
            data=chat_text,
            file_name="wisebuddy_chat.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    # Quote of the day
    st.divider()
    st.subheader("✨ Daily Inspiration")
    quotes = [
        "🌟 Believe you can and you're halfway there.",
        "🚀 Success is the sum of small efforts repeated daily.",
        "💡 The best way to predict the future is to create it.",
        "❤️ You are stronger than you think.",
        "🔥 Dream big. Start small. Act now."
    ]
    st.info(f'"{random.choice(quotes)}"')

# 👉 Main chat interface
st.title("💬 WiseBuddy Chat")
st.caption("Your personal AI advisor for insightful guidance")

# 👉 Chat container
with st.container():
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Chat history display
    st.markdown('<div class="chat-history">', unsafe_allow_html=True)
    
    for msg in st.session_state.chat_history:
        if msg["sender"] == "WiseBuddy":
            st.markdown(f'''
                <div class="bot-message">
                    <div><strong>🤖 WiseBuddy</strong></div>
                    <div>{msg["message"]}</div>
                    <div class="timestamp">{msg["timestamp"]}</div>
                </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown(f'''
                <div class="user-message">
                    <div><strong>👤 You</strong></div>
                    <div>{msg["message"]}</div>
                    <div class="timestamp">{msg["timestamp"]}</div>
                </div>
            ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close chat-history
    
    # Input area
    st.markdown('<div class="chat-input">', unsafe_allow_html=True)
    user_input = st.text_input(
        "Type your message...", 
        key="user_input",
        label_visibility="collapsed",
        placeholder="Ask anything for wise advice..."
    )
    send_button = st.button("Send", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)  # Close chat-input
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close chat-container

# 👉 Handle user input
if send_button and user_input:
    # Add user message to history
    st.session_state.chat_history.append({
        "sender": "You", 
        "message": user_input,
        "timestamp": datetime.now().strftime("%H:%M")
    })
    
    # Clear input field
    st.session_state.user_input = ""
    
    # Show typing indicator
    with st.empty():
        typing_html = '''
            <div class="typing-indicator">
                WiseBuddy is thinking
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
            </div>
        '''
        typing_placeholder = st.markdown(typing_html, unsafe_allow_html=True)
        
        try:
            # Generate response with enhanced prompt
            generation_config = genai.types.GenerationConfig(
                temperature=st.session_state.temperature,
                max_output_tokens=1000
            )
            
            prompt = f"""
            [System Context]
            You are WiseBuddy, a friendly AI advisor specializing in {st.session_state.current_category}.
            The current time is {datetime.now().strftime("%Y-%m-%d %H:%M")}.
            Your responses should be:
            - Kind, supportive and empathetic
            - 2-3 paragraphs maximum
            - Include practical advice when applicable
            - Use simple, accessible language
            - Occasionally include relevant quotes or analogies
            - End with a thoughtful question to continue the conversation
            
            [Conversation History]
            {st.session_state.chat_history[-5:]}
            
            [User's Message]
            {user_input}
            """
            
            response = model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Get response text
            if response.text:
                bot_response = response.text
            else:
                bot_response = "I couldn't generate a response. Could you try asking in a different way?"
                
        except Exception as e:
            bot_response = f"⚠️ I encountered an error: {str(e)}. Please try again."
        
        # Remove typing indicator
        typing_placeholder.empty()
    
    # Add bot response to history
    st.session_state.chat_history.append({
        "sender": "WiseBuddy", 
        "message": bot_response,
        "timestamp": datetime.now().strftime("%H:%M")
    })
    
    # Rerun to update the chat display
    st.rerun()
