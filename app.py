import streamlit as st
import google.generativeai as genai
import random
import time
import os

# 👉 Streamlit Page Setup
st.set_page_config(page_title="WiseBuddy 🧠", page_icon="🤖", layout="centered")

# 👉 API Key Setup - Now in main interface
st.markdown("### 🔑 Gemini API Key Setup")
api_key = st.text_input("Enter your Gemini API key:", type="password", 
                        help="Get your API key from https://aistudio.google.com/app/apikey")

if not api_key:
    st.warning("Please enter your Gemini API key to use WiseBuddy")
    st.markdown("[How to get a Gemini API key](https://aistudio.google.com/app/apikey)")
    st.stop()

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    st.session_state.api_ready = True
except Exception as e:
    st.error(f"API configuration error: {str(e)}")
    st.session_state.api_ready = False
    st.stop()

# 👉 CSS Styling (Improved with better error states)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    .big-font {
        font-size:28px !important;
        font-weight:700;
        color:#2c3e50;
        text-align:center;
        margin-bottom:5px;
        margin-top: 20px;
    }
    
    .subtitle {
        text-align:center;
        color:#6c63ff;
        font-weight:500;
        margin-bottom:20px;
    }
    
    .error-box {
        background: #ffebee;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        border-left: 4px solid #f44336;
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
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
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
    
    .control-panel {
        display: flex;
        gap: 15px;
        margin-bottom: 20px;
        flex-wrap: wrap;
    }
    
    .footer {
        text-align: center;
        margin-top: 30px;
        color: #7b7b7b;
        font-size: 14px;
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
        "is_processing": False
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
            <div style="display:flex;justify-content:flex-end;align-items:flex-end;margin-bottom:15px;">
                <div class="user-bubble">
                    <strong>You:</strong><br>{message}
                </div>
            </div>
        """, unsafe_allow_html=True)
    elif speaker == "bot":
        st.markdown(f"""
            <div style="display:flex;justify-content:flex-start;align-items:flex-end;margin-bottom:15px;">
                <div class="bot-bubble">
                    <strong>WiseBuddy:</strong><br>{message}
                </div>
            </div>
        """, unsafe_allow_html=True)
    elif speaker == "typing":
        st.markdown(f"""
            <div style="display:flex;justify-content:flex-start;align-items:flex-end;margin-bottom:15px;">
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
user_input = st.chat_input("💭 Type your message here...", disabled=not st.session_state.get('api_ready', False))

# 👉 Process User Input
if user_input and not st.session_state.app_state["is_processing"] and st.session_state.get('api_ready', False):
    # Set processing state
    st.session_state.app_state["is_processing"] = True
    st.session_state.app_state["history"].append(("user", user_input))
    st.session_state.app_state["history"].append(("typing", ""))
    st.rerun()

# Process Gemini response after UI update
if st.session_state.app_state.get("is_processing", False) and st.session_state.app_state["history"][-1][0] == "typing" and st.session_state.get('api_ready', False):
    try:
        # Generate system instruction based on category
        system_instruction = f"""
        You are WiseBuddy, a compassionate and insightful AI advisor specializing in {st.session_state.app_state["current_category"]}.
        Your responses should be:
        - Supportive and encouraging
        - Practical and actionable
        - Concise (1-2 paragraphs)
        - Tailored to the user's needs
        
        Current conversation context:
        {st.session_state.app_state["history"][-2][1] if len(st.session_state.app_state["history"]) > 2 else "New conversation"}
        """
        
        # Send message to Gemini
        response = model.generate_content(
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
        st.session_state.app_state["history"].append(("bot", "⚠️ Sorry, I'm having trouble thinking right now. Please try a different question."))
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
