import streamlit as st
import google.generativeai as genai
import random
import time

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
    .big-font { 
        font-size:26px !important; 
        font-weight:bold; 
        color:#2c3e50; 
        margin-bottom: 10px;
    }
    .quote-container {
        background-color:#e6e6fa;
        padding:10px;
        border-radius:10px;
        text-align:center;
        margin-bottom: 20px;
        font-style: italic;
    }
    .user-bubble { 
        background-color:#d1e7dd; 
        padding:12px 15px; 
        border-radius:15px 15px 0 15px; 
        max-width:80%; 
        font-size:16px; 
        margin-left:auto; 
        margin-bottom: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .bot-bubble { 
        background-color:#fff3cd; 
        padding:12px 15px; 
        border-radius:15px 15px 15px 0; 
        max-width:80%; 
        font-size:16px; 
        margin-right:auto; 
        margin-bottom: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .chat-container { 
        height: 60vh;
        overflow-y: auto;
        padding: 15px;
        background-color: #f9f9f9;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 1px solid #e6e6e6;
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
        margin-bottom: 15px;
    }
    .stButton>button:hover {
        background-color: #5a54d4;
    }
    .typing-indicator {
        display: flex;
        align-items: center;
        padding: 10px 15px;
        background-color: #fff3cd;
        border-radius: 15px;
        max-width: 100px;
        margin-bottom: 8px;
    }
    .typing-dot {
        width: 8px;
        height: 8px;
        background-color: #666;
        border-radius: 50%;
        margin: 0 2px;
        animation: typing 1.4s infinite ease-in-out;
    }
    .typing-dot:nth-child(1) { animation-delay: 0s; }
    .typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .typing-dot:nth-child(3) { animation-delay: 0.4s; }
    
    @keyframes typing {
        0%, 60%, 100% { transform: translateY(0); }
        30% { transform: translateY(-5px); }
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
st.markdown(f'<div class="quote-container"><em>{random.choice(quotes)}</em></div>', unsafe_allow_html=True)

# 👉 Initialize session state
def initialize_session():
    return {
        "chat": model.start_chat(history=[]),
        "history": [],
        "current_category": "🌟 Motivation & Positivity",
        "is_processing": False
    }

if "app_state" not in st.session_state:
    st.session_state.app_state = initialize_session()

# 👉 Category Select with persistence
def update_category():
    new_category = st.session_state.category_select
    if new_category != st.session_state.app_state["current_category"]:
        st.session_state.app_state = initialize_session()
        st.session_state.app_state["history"].append(
            ("bot", f"Hello! I'm now your advisor in **{new_category}**. How can I assist you today?")
        )
        st.session_state.app_state["current_category"] = new_category

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
    ].index(st.session_state.app_state["current_category"]),
    key="category_select",
    on_change=update_category
)

# 👉 Clear Chat Button
if st.button("🗑️ Clear Chat", use_container_width=True):
    st.session_state.app_state = initialize_session()
    st.session_state.app_state["history"].append(
        ("bot", f"Hello! I'm WiseBuddy, your AI advisor in **{st.session_state.app_state['current_category']}**. How can I assist you today?")
    )
    st.rerun()

# 👉 Chat Display
chat_container = st.container()
with chat_container:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    for speaker, message in st.session_state.app_state["history"]:
        if speaker == "user":
            st.markdown(f'''
                <div class="user-bubble">
                    <strong>You:</strong><br>{message}
                </div>
            ''', unsafe_allow_html=True)
        elif speaker == "bot":
            st.markdown(f'''
                <div class="bot-bubble">
                    <strong>WiseBuddy 🤖:</strong><br>{message}
                </div>
            ''', unsafe_allow_html=True)
        elif speaker == "typing":
            st.markdown(f'''
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# 👉 User Input
user_input = st.chat_input("💭 Type your message here:")

# 👉 Process User Input
if user_input and not st.session_state.app_state["is_processing"]:
    # Set processing state
    st.session_state.app_state["is_processing"] = True
    st.session_state.app_state["history"].append(("user", user_input))
    st.session_state.app_state["history"].append(("typing", ""))
    st.rerun()

# Process Gemini response after UI update
if st.session_state.app_state.get("is_processing", False) and st.session_state.app_state["history"][-1][0] == "typing":
    try:
        # Generate system instruction based on category
        system_instruction = f"""
        You are WiseBuddy, a compassionate, knowledgeable, and encouraging AI assistant. 
        Your primary role is to provide wise advice and insights specifically in the domain of 
        '{st.session_state.app_state["current_category"]}'.
        
        When responding:
        - Maintain a helpful and positive tone
        - Offer practical advice or thoughtful perspectives
        - Keep answers concise but comprehensive (1-3 paragraphs)
        - Do not break character as WiseBuddy
        - If the question seems outside your scope, gently guide back to your expertise
        - Use emojis sparingly to enhance communication
        """
        
        # Send message to Gemini
        response = st.session_state.app_state["chat"].send_message(
            user_input,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=500
            ),
            system_instruction=system_instruction
        )
        
        # Get response and remove typing indicator
        bot_response = response.text
        st.session_state.app_state["history"].pop()  # Remove typing indicator
        st.session_state.app_state["history"].append(("bot", bot_response))
        
    except Exception as e:
        # Handle errors gracefully
        st.session_state.app_state["history"].pop()  # Remove typing indicator
        st.session_state.app_state["history"].append(("bot", "⚠️ Sorry, I'm having trouble thinking clearly right now. Please try again later."))
        st.error(f"API Error: {str(e)}")
    finally:
        # Reset processing state
        st.session_state.app_state["is_processing"] = False
        st.rerun()
