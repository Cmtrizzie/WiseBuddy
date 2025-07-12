import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import time
from pathlib import Path # Import Path for absolute path handling

# --- Configuration ---
# Determine the base directory of the script to construct the absolute path for .env
# This makes the .env loading more robust, less dependent on where the script is run from.
BASE_DIR = Path(__file__).resolve().parent

# Construct the absolute path to the .env file
DOTENV_PATH = BASE_DIR / ".env"

# --- Debugging Load_dotenv (Updated for absolute path) ---
dotenv_loaded_successfully = False
if DOTENV_PATH.exists():
    print(f"DEBUG: .env file exists at {DOTENV_PATH}") # Print to console for server logs
    st.sidebar.write(f"DEBUG: .env file exists at `{DOTENV_PATH}`") # Print to Streamlit sidebar
    dotenv_loaded_successfully = load_dotenv(dotenv_path=DOTENV_PATH)
else:
    print(f"DEBUG: .env file NOT found at {DOTENV_PATH}") # Print to console
    st.sidebar.write(f"DEBUG: .env file NOT found at `{DOTENV_PATH}`") # Print to Streamlit sidebar

st.sidebar.write(f"DEBUG: .env file loaded? **{dotenv_loaded_successfully}**")
# --- End Debugging ---


# Gemini Model Name
MODEL_NAME = "gemini-1.5-flash"

# WiseBuddy's Persona/System Instruction
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
    GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY") # Use .get() for safety
    if GEMINI_API_KEY:
        st.sidebar.write("DEBUG: API Key found in Streamlit Secrets.")
    else:
        st.sidebar.write("DEBUG: API Key NOT found in Streamlit Secrets. Checking environment variables.")
except Exception as e: # Catch any error from st.secrets access
    st.sidebar.write(f"DEBUG: Error accessing st.secrets: {e}")
    GEMINI_API_KEY = None # Ensure it's None if secrets access fails

# Fallback to environment variable (for local testing)
if not GEMINI_API_KEY:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if GEMINI_API_KEY:
        st.sidebar.write("DEBUG: API Key found via os.getenv().")
    else:
        st.sidebar.write("DEBUG: API Key NOT found via os.getenv().")


# --- Final check and stop if key is missing ---
if not GEMINI_API_KEY:
    st.error("🚨 Gemini API key not found. Please set `GEMINI_API_KEY` in your environment variables or Streamlit Secrets.")
    st.info(f"For local development, ensure a `.env` file exists at `{DOTENV_PATH}` with `GEMINI_API_KEY='YOUR_API_KEY'`.")
    st.info("For Streamlit Cloud deployment, add `GEMINI_API_KEY` to your app's secrets.")
    st.stop() # Stop the app if no API key is found
else:
    st.sidebar.success("DEBUG: Gemini API Key successfully loaded! 🎉") # Indicates success
    # For extra debugging, uncomment the line below to see a partial key value
    # st.sidebar.write(f"DEBUG: Loaded Key Value (first 5 chars): {GEMINI_API_KEY[:5]}...")


genai.configure(api_key=GEMINI_API_KEY)

# --- Model Initialization ---
model = genai.GenerativeModel(MODEL_NAME, system_instruction=SYSTEM_INSTRUCTION)

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_session" not in st.session_state or not st.session_state.messages:
    st.session_state.chat_session = model.start_chat(history=[])

# --- Helper Function for Gemini API Call ---
def generate_gemini_response(prompt_text, max_retries=3, delay=1):
    for attempt in range(max_retries):
        try:
            response = st.session_state.chat_session.send_message(prompt_text)
            return response.text
        except genai.types.BlockedPromptException as e:
            st.error("WiseBuddy detected potentially harmful content. Please try rephrasing your query.")
            st.exception(e)
            return "I cannot respond to that query as it might violate safety guidelines. Please try asking something else."
        except Exception as e:
            if attempt < max_retries - 1:
                st.warning(f"API call failed, retrying in {delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)
                delay *= 2
            else:
                st.error(f"WiseBuddy encountered an error: {e}. Please try again later.")
                st.exception(e)
                return "Oops! WiseBuddy encountered an issue and couldn't respond. Please try again."
    return "An unexpected error occurred after multiple retries."

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
if prompt := st.chat_input("Ask WiseBuddy anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("model"):
        with st.status("WiseBuddy is thinking...", expanded=False) as status_box:
            status_box.write("Connecting to Gemini...")
            response_text = generate_gemini_response(prompt)
            if "Oops!" not in response_text and "cannot respond" not in response_text:
                 status_box.update(label="WiseBuddy replied!", state="complete", expanded=False)
            else:
                 status_box.update(label="WiseBuddy encountered an issue.", state="error", expanded=False)

        st.markdown(response_text)

    st.session_state.messages.append({"role": "model", "content": response_text})
