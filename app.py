import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import time # For simulating a small delay, if desired, or for retries

# --- Configuration ---
# Load environment variables (for local development)
load_dotenv()

# Gemini Model Name
MODEL_NAME = "gemini-1.5-flash"

# WiseBuddy's Persona/System Instruction
# This helps guide the model's behavior and tone.
SYSTEM_INSTRUCTION = """
You are WiseBuddy, a friendly, helpful, and knowledgeable AI assistant.
Your goal is to provide concise, accurate, and relevant information.
Maintain a positive and approachable tone.
If you don't know the answer, politely state that you cannot provide information on that topic.
Always prioritize user safety and ethical responses.
"""

# --- API Key Management ---
# Attempt to get API key from Streamlit Secrets (for deployment)
# Fallback to environment variable (for local testing)
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    st.error("🚨 Gemini API key not found. Please set `GEMINI_API_KEY` in your environment variables or Streamlit Secrets.")
    st.info("For local development, create a `.env` file in your project directory with `GEMINI_API_KEY='YOUR_API_KEY'`.")
    st.info("For Streamlit Cloud deployment, add `GEMINI_API_KEY` to your app's secrets.")
    st.stop() # Stop the app if no API key is found

genai.configure(api_key=GEMINI_API_KEY)

# --- Model Initialization ---
# Initialize the generative model with the system instruction
model = genai.GenerativeModel(MODEL_NAME, system_instruction=SYSTEM_INSTRUCTION)

# --- Session State Initialization ---
# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize chat session (important for multi-turn conversations)
# This will be re-created if history is cleared or on first run.
if "chat_session" not in st.session_state or not st.session_state.messages:
    # If starting fresh or cleared, create a new chat session
    st.session_state.chat_session = model.start_chat(history=[]) # Start with empty history

# --- Helper Function for Gemini API Call ---
def generate_gemini_response(prompt_text, max_retries=3, delay=1):
    """
    Generates a response from Gemini API with retry logic.
    Args:
        prompt_text (str): The user's input prompt.
        max_retries (int): Maximum number of retries for API calls.
        delay (int): Initial delay in seconds before retrying (exponential backoff).
    Returns:
        str: The generated response text from Gemini.
    """
    for attempt in range(max_retries):
        try:
            # We already started the chat_session with history.
            # Now, just send the current user message to continue the conversation.
            response = st.session_state.chat_session.send_message(prompt_text)
            return response.text
        except genai.types.BlockedPromptException as e:
            st.error("WiseBuddy detected potentially harmful content. Please try rephrasing your query.")
            st.exception(e) # Log the full exception for debugging
            return "I cannot respond to that query as it might violate safety guidelines. Please try asking something else."
        except Exception as e:
            if attempt < max_retries - 1:
                st.warning(f"API call failed, retrying in {delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)
                delay *= 2 # Exponential backoff
            else:
                st.error(f"WiseBuddy encountered an error: {e}. Please try again later.")
                st.exception(e) # Log the full exception for debugging
                return "Oops! WiseBuddy encountered an issue and couldn't respond. Please try again."
    return "An unexpected error occurred after multiple retries." # Should not be reached

# --- Streamlit UI ---
st.set_page_config(page_title="WiseBuddy - Your AI Chat Assistant", page_icon="💡", layout="centered")
st.title("💡 WiseBuddy")
st.markdown("Your intelligent AI chat assistant, powered by Gemini 1.5 Flash.")

# Custom CSS for a cleaner look (optional)
st.markdown("""
<style>
    .st-chat-message-user {
        background-color: #e0f7fa; /* Light blue for user */
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 8px;
    }
    .st-chat-message-model {
        background-color: #f0f0f0; /* Light grey for model */
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 8px;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50; /* Green */
        color: white;
        border-radius: 10px;
        padding: 10px;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    /* Adjust input field appearance */
    .stTextInput>div>div>input {
        border-radius: 10px;
        padding: 10px;
    }
    /* Specific styles for Streamlit chat elements */
    [data-testid="stChatMessage"] {
        padding: 0.5rem 1rem;
        margin-bottom: 0.5rem;
    }
    [data-testid="stVerticalBlock"] div:has(div.element-container) {
        gap: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


# --- New Chat Button ---
if st.button("✨ Start a New Chat", help="Clear current conversation and start fresh"):
    st.session_state.messages = []
    st.session_state.chat_session = model.start_chat(history=[]) # Re-initialize chat session
    st.experimental_rerun() # Rerun to clear display immediately

# Display existing chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- User Input and Model Response Logic ---
# Using st.chat_input for the main input field at the bottom
if prompt := st.chat_input("Ask WiseBuddy anything..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response from Gemini
    with st.chat_message("model"):
        with st.status("WiseBuddy is thinking...", expanded=False) as status_box:
            # Update history within the status context if needed for debugging
            # For Gemini, the chat_session itself manages its history internally
            status_box.write("Connecting to Gemini...")
            response_text = generate_gemini_response(prompt)
            if "Oops!" not in response_text and "cannot respond" not in response_text: # Check if it's an error message
                 status_box.update(label="WiseBuddy replied!", state="complete", expanded=False)
            else:
                 status_box.update(label="WiseBuddy encountered an issue.", state="error", expanded=False)

        st.markdown(response_text)

    # Add model response to chat history
    st.session_state.messages.append({"role": "model", "content": response_text})

