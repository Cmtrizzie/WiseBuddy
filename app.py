import streamlit as st
import google.generativeai as genai
import random
import time

# 👉 Configure your Gemini API Key
genai.configure(api_key="AIzaSyCCrH9lwWQcH38Vbv287H-CTPXaR5U_lF4")
model = genai.GenerativeModel('gemini-1.5-flash')

# 👉 Streamlit Page Setup
st.set_page_config(page_title="WiseBuddy 🧠", page_icon="🤖", layout="centered")

# 👉 CSS Styling (Improved with animations, gradients, and better spacing)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    body {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4edf5 100%);
        background-attachment: fixed;
    }
    
    .container {
        max-width: 800px;
        margin: 0 auto;
        padding: 0 20px;
    }
    
    .big-font {
        font-size: 28px !important;
        font-weight: 700;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 5px;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.1);
    }
    
    .subtitle {
        text-align: center;
        color: #6c63ff;
        font-weight: 500;
        margin-bottom: 20px;
    }
    
    .quote-container {
        background: linear-gradient(135deg, #e6e6fa 0%, #d6cbfa 100%);
        padding: 15px;
        border-radius: 18px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(108, 99, 255, 0.15);
        border: 1px solid rgba(108, 99, 255, 0.1);
    }
    
    .quote-text {
        font-style: italic;
        font-size: 16px;
        color: #4a4a7d;
        margin: 0;
    }
    
    .chat-container {
        background: white;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.08);
        margin-bottom: 20px;
        border: 1px solid rgba(0,0,0,0.05);
    }
    
    .message-area {
        height: 55vh;
        overflow-y: auto;
        padding: 15px;
        margin-bottom: 20px;
        background: #fafaff;
        border-radius: 15px;
        border: 1px solid rgba(0,0,0,0.03);
    }
    
    .user-bubble {
        background: linear-gradient(135deg, #d0f0c0 0%, #b8e994 100%);
        padding: 16px 20px;
        border-radius: 24px 24px 0 24px;
        max-width: 80%;
        font-size: 16px;
        margin-left: auto;
        margin-bottom: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        position: relative;
        animation: fadeIn 0.3s ease-out;
        color: #2d3436;
    }
    
    .bot-bubble {
        background: linear-gradient(135deg, #e0d4f7 0%, #cbb2fe 100%);
        padding: 16px 20px;
        border-radius: 24px 24px 24px 0;
        max-width: 80%;
        font-size: 16px;
        margin-right: auto;
        margin-bottom: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        position: relative;
        animation: fadeIn 0.3s ease-out;
        color: #2d3436;
    }
    
    .user-bubble::after, .bot-bubble::after {
        content: "";
        position: absolute;
        bottom: -8px;
        width: 20px;
        height: 20px;
        background-size: cover;
    }
    
    .user-bubble::after {
        right: 0;
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="%23b8e994"><path d="M10 20s10-8 0-20c-10 12 0 20 0 20z"/></svg>');
    }
    
    .bot-bubble::after {
        left: 0;
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="%23cbb2fe"><path d="M10 20S0 12 10 0c10 12 0 20 0 20z"/></svg>');
    }
    
    .avatar {
        width: 42px;
        height: 42px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        color: white;
        margin: 0 10px;
        flex-shrink: 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .user-avatar { 
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
    }
    
    .bot-avatar { 
        background: linear-gradient(135deg, #6c63ff 0%, #4a43cb 100%);
    }
    
    .typing-indicator {
        display: flex;
        align-items: center;
        padding: 12px 18px;
        background: linear-gradient(135deg, #e0d4f7 0%, #cbb2fe 100%);
        border-radius: 24px 24px 24px 0;
        max-width: 120px;
        margin-right: auto;
        margin-bottom: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
    }
    
    .typing-dot {
        width: 10px;
        height: 10px;
        background-color: #6c63ff;
        border-radius: 50%;
        margin: 0 3px;
        animation: typing 1.4s infinite ease-in-out;
    }
    
    .typing-dot:nth-child(1) { animation-delay: 0s; }
    .typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .typing-dot:nth-child(3) { animation-delay: 0.4s; }
    
    @keyframes typing {
        0%, 60%, 100% { transform: translateY(0); }
        30% { transform: translateY(-8px); }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .control-panel {
        display: flex;
        gap: 15px;
        margin-bottom: 20px;
        flex-wrap: wrap;
    }
    
    .stSelectbox {
        flex-grow: 1;
        min-width: 250px;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #6c63ff 0%, #4a43cb 100%);
        color: white;
        border-radius: 12px;
        border: none;
        padding: 10px 20px;
        font-size: 15px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s;
        box-shadow: 0 4px 10px rgba(108, 99, 255, 0.3);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(108, 99, 255, 0.4);
    }
    
    .stButton>button:active {
        transform: translateY(0);
    }
    
    .stTextInput>div>div>input {
        border-radius: 15px !important;
        padding: 12px 18px !important;
        border: 1px solid #ddd !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #6c63ff !important;
        box-shadow: 0 0 0 2px rgba(108, 99, 255, 0.2) !important;
    }
    
    .footer {
        text-align: center;
        margin-top: 30px;
        color: #7b7b7b;
        font-size: 14px;
    }
    </style>
""", unsafe_allow_html=True)

# 👉 Title + Quote
st.markdown('<p class="big-font">💬 WiseBuddy 🧠</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Your AI companion for thoughtful advice</p>', unsafe_allow_html=True)

quotes = [
    "🌟 Believe you can and you're halfway there.",
    "🚀 Success is the sum of small efforts repeated daily.",
    "💡 The best way to predict the future is to create it.",
    "❤️ You are stronger than you think.",
    "🔥 Dream big. Start small. Act now.",
    "🌱 Growth begins at the end of your comfort zone.",
    "🌈 After every storm comes a rainbow of possibilities."
]
st.markdown(f"""
    <div class="quote-container">
        <p class="quote-text">{random.choice(quotes)}</p>
    </div>
""", unsafe_allow_html=True)

# 👉 Initialize Chat State
def initialize_chat():
    return {
        "history": [],
        "current_category": "🌟 Motivation & Positivity",
        "is_processing": False,
        "chat_session": model.start_chat(history=[])
    }

if "app_state" not in st.session_state:
    st.session_state.app_state = initialize_chat()

# 👉 Control Panel
with st.container():
    st.markdown('<div class="control-panel">', unsafe_allow_html=True)
    
    # Category Select
    new_category = st.selectbox(
        "📝 Choose your advice style:",
        options=[
            "🌟 Motivation & Positivity",
            "💡 Business & Wealth",
            "❤️ Love & Relationships",
            "🧘 Mindfulness & Peace",
            "🎯 Goal Setting",
            "🔄 Life Transitions"
        ],
        index=[
            "🌟 Motivation & Positivity",
            "💡 Business & Wealth",
            "❤️ Love & Relationships",
            "🧘 Mindfulness & Peace",
            "🎯 Goal Setting",
            "🔄 Life Transitions"
        ].index(st.session_state.app_state["current_category"]),
        key="category_select"
    )
    
    # Clear Chat Button
    if st.button("🗑️ Clear Chat", key="clear_chat"):
        st.session_state.app_state = initialize_chat()
        st.session_state.app_state["history"].append(
            ("bot", f"Hello! I'm WiseBuddy, your AI advisor in **{st.session_state.app_state['current_category']}**. How can I assist you today?")
        )
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# 👉 Update category if changed
if new_category != st.session_state.app_state["current_category"]:
    st.session_state.app_state["current_category"] = new_category
    st.session_state.app_state["history"].append(
        ("bot", f"Switching to **{new_category}** mode! How can I help you in this area?")
    )

# 👉 Chat Display
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
st.markdown('<div class="message-area">', unsafe_allow_html=True)

if not st.session_state.app_state["history"]:
    st.session_state.app_state["history"].append(
        ("bot", f"Hello! I'm WiseBuddy, your AI advisor in **{st.session_state.app_state['current_category']}**. How can I assist you today?")
    )

for speaker, message in st.session_state.app_state["history"]:
    if speaker == "user":
        st.markdown(f"""
            <div style="display: flex; justify-content: flex-end; align-items: flex-end; margin-bottom: 15px;">
                <div class="user-bubble">
                    <strong>You:</strong><br>{message}
                </div>
                <div class="avatar user-avatar">🧑</div>
            </div>
        """, unsafe_allow_html=True)
    elif speaker == "bot":
        st.markdown(f"""
            <div style="display: flex; justify-content: flex-start; align-items: flex-end; margin-bottom: 15px;">
                <div class="avatar bot-avatar">🤖</div>
                <div class="bot-bubble">
                    <strong>WiseBuddy:</strong><br>{message}
                </div>
            </div>
        """, unsafe_allow_html=True)
    elif speaker == "typing":
        st.markdown(f"""
            <div style="display: flex; justify-content: flex-start; align-items: flex-end; margin-bottom: 15px;">
                <div class="avatar bot-avatar">🤖</div>
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # Close message-area
st.markdown('</div>', unsafe_allow_html=True)  # Close chat-container

# 👉 User Input
user_input = st.chat_input("💭 Type your message here...")

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
        You are WiseBuddy, a compassionate and insightful AI advisor specializing in {st.session_state.app_state["current_category"]}.
        Your responses should be:
        - Supportive and encouraging
        - Practical and actionable
        - Concise (1-2 paragraphs)
        - Tailored to the user's needs
        - Include an emoji when appropriate
        
        Current conversation context:
        {st.session_state.app_state["history"][-2][1] if len(st.session_state.app_state["history"]) > 2 else "New conversation"}
        """
        
        # Send message to Gemini
        response = st.session_state.app_state["chat_session"].send_message(
            user_input,
            generation_config=genai.types.GenerationConfig(
                temperature=0.8,
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

# 👉 Footer
st.markdown("""
    <div class="footer">
        WiseBuddy 🧠 • Your AI companion for thoughtful advice • Powered by Gemini
    </div>
""", unsafe_allow_html=True)
