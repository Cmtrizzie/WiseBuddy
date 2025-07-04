import streamlit as st
import google.generativeai as genai
import random

# 👉 Configure your actual Gemini API key - Use Streamlit Secrets for production!
# For local testing, you can temporarily put it here, but st.secrets is best.
# genai.configure(api_key=st.secrets["GEMINI_API_KEY"]) # Ideal for deployment
genai.configure(api_key="AIzaSyCCrH9lwWQcH38Vbv287H-CTPXaR5U_lF4") # For quick local testing, replace this

model = genai.GenerativeModel('gemini-1.5-flash')

# 👉 Streamlit page setup
st.set_page_config(page_title="WiseBuddy 🧠", page_icon="🤖", layout="centered")

# 👉 CSS Styling
st.markdown("""
    <style>
    .big-font { font-size:26px !important; font-weight:bold; color:#2c3e50; }
    .advice-box { background-color:#fff; padding:15px; border-radius:10px; box-shadow:0 4px 8px rgba(0,0,0,0.1); color:#333; font-size:17px; margin-top:10px; }
    .user-bubble { 
        background-color:#d1e7dd; 
        padding:12px 15px; 
        border-radius:15px; 
        max-width:70%; 
        font-size:16px; 
        margin-left:auto; 
        align-self: flex-end; /* Align to the right */
        word-wrap: break-word; /* Ensure text wraps */
    }
    .bot-bubble { 
        background-color:#fff3cd; 
        padding:12px 15px; 
        border-radius:15px; 
        max-width:70%; 
        font-size:16px; 
        margin-right:auto; 
        align-self: flex-start; /* Align to the left */
        word-wrap: break-word; /* Ensure text wraps */
    }
    .chat-container { 
        display:flex; 
        flex-direction:column; 
        gap:10px; 
        margin-top:10px; 
        height: 60vh; /* Fixed height for chat area */
        overflow-y: auto; /* Scrollable */
        padding-right: 10px; /* Space for scrollbar */
    }
    .stSelectbox label {
        font-weight: bold;
        color: #2c3e50;
    }
    .stButton>button {
        background-color: #6c63ff;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 8px 15px;
        font-size: 15px;
        cursor: pointer;
        transition: background-color 0.3s;
    }
    .stButton>button:hover {
        background-color: #5a54d4;
    }
    </style>
""", unsafe_allow_html=True)

# 👉 Title + Quote of the Day
st.markdown('<p class="big-font">💬 Welcome to <span style="color:#6c63ff;">WiseBuddy</span> 🧠</p>', unsafe_allow_html=True)

quotes = [
    "🌟 Believe you can and you're halfway there.",
    "🚀 Success is the sum of small efforts repeated daily.",
    "💡 The best way to predict the future is to create it.",
    "❤️ You are stronger than you think.",
    "🔥 Dream big. Start small. Act now."
]
st.markdown(f'<div style="background-color:#e6e6fa;padding:10px;border-radius:10px;text-align:center;"><em>{random.choice(quotes)}</em></div>', unsafe_allow_html=True)

# 👉 Initialize Chat History and Category
if 'chat' not in st.session_state:
    st.session_state.chat = None # Will be initialized on first run or clear
if 'history' not in st.session_state:
    st.session_state.history = []
if 'current_category' not in st.session_state:
    st.session_state.current_category = "🌟 Motivation & Positivity"

# 👉 Function to initialize/clear chat
def initialize_chat_session():
    st.session_state.chat = model.start_chat(history=[])
    st.session_state.history = [("bot", f"Hello! I'm WiseBuddy, your AI advisor in **{st.session_state.current_category}**. How can I assist you today?")]
    # Note: The above initial bot message is *not* sent to the model's history,
    # as start_chat() creates a fresh history for the model. This is just for display.

# Initialize chat if not exists or if category changed recently (handled by update_category)
if st.session_state.chat is None or st.session_state.history == []:
    initialize_chat_session()

# 👉 Category Select with persistence
def update_category():
    old_category = st.session_state.current_category
    new_category = st.session_state.category_select
    
    if old_category != new_category:
        st.session_state.current_category = new_category
        # Clear chat when category changes for a fresh start
        initialize_chat_session()
    
category = st.selectbox(
    "📝 Choose your advice style:",
    options=[
        "🌟 Motivation & Positivity",
        "💡 Business & Wealth",
        "❤️ Love & Relationships",
        "🧘 Mindfulness & Peace"
    ],
    index=[
        "🌟 Motivation & Positivity",
        "💡 Business & Wealth",
        "❤️ Love & Relationships",
        "🧘 Mindfulness & Peace"
    ].index(st.session_state.current_category),
    key="category_select",
    on_change=update_category
)

# 👉 Clear Chat Button
if st.button("🗑️ Clear Chat"):
    initialize_chat_session()
    st.rerun() # Rerun to reflect the cleared chat immediately

# 👉 Display Chat History
chat_container = st.container(height=400, border=True) # Use a fixed height container
with chat_container:
    # We don't need the outer <div> with chat-container class here if st.container is used
    # But the inner bubbles still use their styles
    for speaker, message in st.session_state.history:
        if speaker == "user":
            st.markdown(f'''
                <div class="user-bubble">
                    <strong>You:</strong><br>{message}
                </div>
            ''', unsafe_allow_html=True)
        else: # speaker == "bot"
            st.markdown(f'''
                <div class="bot-bubble">
                    <strong>WiseBuddy 🤖:</strong><br>{message}
                </div>
            ''', unsafe_allow_html=True)

# 👉 User Input
user_input = st.chat_input("💭 Type your message here:")

# 👉 Process User Input
if user_input:
    # Add user message to history
    st.session_state.history.append(("user", user_input))
    
    # Add a temporary "thinking" message from bot
    st.session_state.history.append(("bot", "WiseBuddy is thinking... 🤔"))
    
    # Rerun to show user message and thinking message immediately
    st.rerun() 

# This part runs AFTER rerun, so it will execute after the above block
# when the app reruns. We need to ensure it only runs once per input.
if user_input and st.session_state.history[-1][1] == "WiseBuddy is thinking... 🤔":
    
    # Generate context-aware prompt
    # The ChatSession itself maintains the history for the model.
    # We only need to guide its persona and the current intent.
    system_instruction = f"""
    You are WiseBuddy, a compassionate, knowledgeable, and encouraging AI assistant. 
    Your primary role is to provide wise advice and insights specifically in the domain of 
    '{st.session_state.current_category}'.
    
    When responding:
    - Maintain a helpful and positive tone.
    - Offer practical advice or thoughtful perspectives.
    - Keep answers concise but comprehensive.
    - Do not break character as WiseBuddy.
    - If the user's question seems outside your scope for the chosen category, gently guide them back or suggest changing categories.
    """
    
    try:
        with st.spinner("WiseBuddy is crafting wisdom..."):
            # Send message to the model. The chat session handles its internal history.
            response = st.session_state.chat.send_message(user_input, 
                                                        generation_config={'temperature': 0.7}, # Adjust creativity
                                                        stream=False) # For now, no streaming
            bot_response = response.text
            
            # Replace the "thinking" message with the actual response
            st.session_state.history[-1] = ("bot", bot_response)
            
    except Exception as e:
        st.error(f"WiseBuddy encountered an issue: {e}. Please try again or clear chat.")
        # Revert the "thinking" message to an error or similar
        st.session_state.history[-1] = ("bot", "Oops! WiseBuddy had a momentary lapse. Please try again.")
        
    # Rerun to update chat display with the actual response or error
    st.rerun()

