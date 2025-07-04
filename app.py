import streamlit as st
import google.generativeai as genai
import random
import time

# 👉 Streamlit Page Setup
st.set_page_config(page_title="WiseBuddy 🧠", page_icon="🤖", layout="centered")

# 👉 API Key Setup
st.markdown("### 🔑 Gemini API Key Setup")
api_key = st.text_input("Enter your Gemini API key:", type="password",
                        help="Get your API key from https://aistudio.google.com/app/apikey",
                        key="api_key_input")

# Initialize model and API readiness in session state
if "model_instance" not in st.session_state:
    st.session_state.model_instance = None
if "api_ready" not in st.session_state:
    st.session_state.api_ready = False
if "model_initialized" not in st.session_state:
    st.session_state.model_initialized = False

# Only configure API if key is provided and model not already initialized
if api_key and not st.session_state.model_initialized:
    try:
        genai.configure(api_key=api_key)

        # Define the base system instruction for the model instance
        # This global instruction sets the core persona of WiseBuddy.
        # Category-specific instructions will be handled by priming the chat history.
        base_system_instruction = (
            "You are WiseBuddy, a compassionate, knowledgeable, and encouraging AI assistant. "
            "Your primary role is to provide wise advice and insights based on the user's chosen category."
        )

        # Initialize the GenerativeModel with the base system instruction
        temp_model_instance = genai.GenerativeModel(
            'gemini-1.5-flash',
            system_instruction=base_system_instruction # <-- Correct place for system_instruction
        )
        
        # Test the API connection with a simple content generation
        test_response = temp_model_instance.generate_content("Hello, can you help me?", stream=False)
        
        # Check if text response exists, indicating successful connection
        if test_response and test_response.text:
            st.session_state.model_instance = temp_model_instance # Store the configured model
            st.session_state.api_ready = True
            st.session_state.model_initialized = True # Mark as initialized
            st.success("✅ API connected successfully!")
        else:
            # If no text, check if it was blocked by safety settings
            feedback = test_response.prompt_feedback if test_response else None
            if feedback and feedback.block_reason:
                error_msg = f"API test failed: Content blocked due to {feedback.block_reason.name}."
            else:
                error_msg = "API test failed: No valid response received. Check API key or connection."
            raise ValueError(error_msg)
            
    except Exception as e:
        st.error(f"❌ API configuration error: {str(e)}")
        st.error("Please check your Gemini API key, it might be incorrect or have issues.")
        st.session_state.api_ready = False
        st.session_state.model_initialized = False # Reset flag
        st.session_state.model_instance = None # Reset model if error
        
elif not api_key:
    st.warning("⚠️ Please enter your Gemini API key to use WiseBuddy")
    st.markdown("[How to get a Gemini API key](https://aistudio.google.com/app/apikey)")
    st.stop() # Stop execution if API key is not ready

# Stop further execution if API is not ready
if not st.session_state.api_ready:
    st.stop()


# 👉 CSS Styling (same as your previous version, keeping for completeness)
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
        margin-top: 0px;
    }
    
    .subtitle {
        text-align:center;
        color:#6c63ff;
        font-weight:500;
        margin-bottom:20px;
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
def initialize_chat_state():
    return {
        "history": [], # For displaying chat in Streamlit
        "current_category": "🌟 Motivation & Positivity",
        "is_processing": False,
        "chat_session": None # The actual genai.ChatSession object
    }

if "app_state" not in st.session_state:
    st.session_state.app_state = initialize_chat_state()

# Helper function to start/reset the Gemini chat session
def start_new_gemini_chat():
    if st.session_state.api_ready and st.session_state.model_instance:
        # This initial user message primes the chat session with the category context.
        # The model_instance itself already has the base system_instruction.
        category_priming_prompt = (
            f"From now on, provide advice in the style of '{st.session_state.app_state['current_category']}'. "
            "Keep your responses supportive, encouraging, practical, and concise (1-3 paragraphs). "
            "If a question falls outside this category, gently guide the user back or suggest a category change."
        )

        st.session_state.app_state["chat_session"] = st.session_state.model_instance.start_chat(
            history=[
                {"role": "user", "parts": [category_priming_prompt]},
                {"role": "model", "parts": ["Understood! I'm ready to provide advice in this area. How can I help?"]}
            ]
        )
    else:
        st.session_state.app_state["chat_session"] = None

# Initialize the chat session if it's not set up yet or on initial load
if st.session_state.api_ready and st.session_state.app_state["chat_session"] is None:
    start_new_gemini_chat()
    # This is the message displayed to the user for the very first interaction
    st.session_state.app_state["history"].append(
        ("bot", f"Hello! I'm WiseBuddy, your AI advisor in **{st.session_state.app_state['current_category']}**. How can I assist you today?")
    )


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
        st.session_state.app_state = initialize_chat_state() # Reset all app state
        start_new_gemini_chat() # Start a new Gemini chat session with initial priming
        st.session_state.app_state["history"].append(
            ("bot", f"Hello! I'm WiseBuddy, your AI advisor in **{st.session_state.app_state['current_category']}**. How can I assist you today?")
        )
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# 👉 Update category if changed
if new_category != st.session_state.app_state["current_category"]:
    st.session_state.app_state["current_category"] = new_category
    start_new_gemini_chat() # Start a new chat session with the new category priming
    st.session_state.app_state["history"].append(
        ("bot", f"Switching to **{new_category}** mode! How can I help you in this area?")
    )

# 👉 Chat Display
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
st.markdown('<div class="message-area">', unsafe_allow_html=True)

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
user_input = st.chat_input("💭 Type your message here...", disabled=not st.session_state.api_ready)

# 👉 Process User Input
if user_input and not st.session_state.app_state["is_processing"] and st.session_state.api_ready:
    # Set processing state
    st.session_state.app_state["is_processing"] = True
    st.session_state.app_state["history"].append(("user", user_input))
    st.session_state.app_state["history"].append(("typing", ""))
    st.rerun() # Rerun to display user message and typing indicator

# Process Gemini response after UI update
# This block will run on the rerun triggered by the user_input block
if st.session_state.app_state.get("is_processing", False) and st.session_state.app_state["history"] and st.session_state.app_state["history"][-1][0] == "typing" and st.session_state.api_ready:
    try:
        # Get the actual ChatSession object
        chat_session = st.session_state.app_state["chat_session"]
        
        if chat_session:
            # Send the user input to the chat session
            response = chat_session.send_message(
                user_input, # The input from the user
                generation_config=genai.types.GenerationConfig(
                    temperature=0.8,
                    max_output_tokens=500
                )
            )
            
            bot_response = ""
            if response.text:
                bot_response = response.text
            elif response.candidates: # If response.text is empty, check candidates for block reasons
                feedback = response.prompt_feedback
                if feedback and feedback.block_reason:
                    bot_response = f"WiseBuddy cannot respond to that due to content policy: {feedback.block_reason.name}. Please try something else."
                else:
                    # Fallback if no text but candidates exist without block reason (unlikely for text-only model)
                    bot_response = "WiseBuddy had trouble generating a text response. Could you rephrase?"
            else:
                # Catch-all for truly empty or malformed responses
                bot_response = "WiseBuddy had an unexpected issue. Please try again."

            # Remove typing indicator and append bot response
            st.session_state.app_state["history"].pop()
            st.session_state.app_state["history"].append(("bot", bot_response))
        else:
            # This case should ideally not happen if api_ready is True
            st.session_state.app_state["history"].pop() # Remove typing
            st.session_state.app_state["history"].append(("bot", "WiseBuddy is not ready. Please ensure your API key is correct and try refreshing."))
            
    except Exception as e:
        # Handle API or other unexpected errors
        st.session_state.app_state["history"].pop() # Remove typing
        # Provide a more user-friendly error
        display_error = str(e).split('\n')[0] # Get first line of error
        if "Blocked by safety settings" in display_error:
             display_error = "Response blocked by safety settings."
        elif "quota" in display_error.lower():
            display_error = "API quota exceeded. Please try again later."
        elif "auth" in display_error.lower() or "authentication" in display_error.lower():
            display_error = "Authentication error with API key. Please check your key."

        st.session_state.app_state["history"].append(("bot", f"⚠️ Sorry, an error occurred: {display_error}. Please try again."))
        st.error(f"Error during content generation: {str(e)}") # Log full error for debugging
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
