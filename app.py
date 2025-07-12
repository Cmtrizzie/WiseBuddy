import streamlit as st
import google.generativeai as genai
import os
import time
from pathlib import Path
from datetime import datetime
import pytz # For time zone handling

# --- Configuration & Environment Setup ---
# Determine the base directory of the script for robust .env loading
BASE_DIR = Path(__file__).resolve().parent

# Gemini Model Name
MODEL_NAME = "gemini-1.5-flash"

# WiseBuddy's Persona/System Instruction
SYSTEM_INSTRUCTION = """
You are WiseBuddy, a friendly, empathetic, and highly knowledgeable AI assistant.
Your primary goal is to provide concise, accurate, and relevant information.
Maintain a positive, approachable, and slightly encouraging tone.
Always strive to be helpful and provide clear, easy-to-understand explanations.
If you don't know the answer, politely state that you cannot provide information on that specific topic or suggest where the user might find it.
Prioritize user safety and ensure all responses are ethical and respectful.
You can also use tools to get real-world information if needed.
"""

# --- Tool Definitions (for Function Calling) ---
# Define a function for getting current time and date in a specific timezone
def get_current_datetime_kasese(timezone: str = "Africa/Kampala"):
    """
    Returns the current date and time in a specified timezone.
    Defaults to the timezone of Kasese, Western Region, Uganda (Africa/Kampala).
    """
    try:
        tz = pytz.timezone(timezone)
        now = datetime.now(tz)
        return now.strftime("The current date in %s is %Y-%m-%d and the time is %H:%M:%S." % timezone)
    except pytz.UnknownTimeZoneError:
        return f"Error: Unknown timezone '{timezone}'. Please provide a valid timezone, e.g., 'America/New_York', 'Europe/London'."

# Create a list of tools for the model
tools = [
    genai.GenerativeModel.Tool(
        function_declarations=[
            get_current_datetime_kasese
        ]
    )
]

# --- API Key Management ---
GEMINI_API_KEY = None
try:
    GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")
except Exception:
    pass # st.secrets not available, fall back to os.getenv()

if not GEMINI_API_KEY:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    st.error("🚨 Gemini API key not found. Please set `GEMINI_API_KEY` in your Streamlit Cloud secrets.")
    st.info("For Streamlit Cloud deployment, add `GEMINI_API_KEY` to your app's secrets.")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)

# --- Model Initialization ---
# Initialize the generative model with the system instruction and tools
model = genai.GenerativeModel(MODEL_NAME, system_instruction=SYSTEM_INSTRUCTION, tools=tools)

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_session" not in st.session_state:
    st.session_state.chat_session = None # Initialize as None, create on first message or new chat

# Create a new chat session only if it doesn't exist or is reset
if st.session_state.chat_session is None or not st.session_state.messages:
    # Pass existing history if any, but ensure tools are included for new chat sessions
    st.session_state.chat_session = model.start_chat(history=st.session_state.messages)

# --- Helper Function for Gemini API Call with Streaming & Function Calling ---
def process_gemini_response(prompt_text, max_retries=3, delay=1):
    """
    Generates a response from Gemini API with retry logic, streaming, and function calling.
    """
    for attempt in range(max_retries):
        try:
            # Send the user's message to the chat session
            response_generator = st.session_state.chat_session.send_message(prompt_text, stream=True)

            full_response_content = ""
            for chunk in response_generator:
                if chunk.text:
                    full_response_content += chunk.text
                    # Display chunks as they arrive for streaming effect
                    yield chunk.text
                if chunk.tool_calls:
                    # Handle tool calls if the model requests them
                    for tool_call in chunk.tool_calls:
                        function_name = tool_call.function.name
                        function_args = tool_call.function.args

                        st.write(f"DEBUG: Model called function: {function_name} with args: {function_args}") # Debugging tool calls
                        # Check if the function exists in our defined tools
                        if function_name == "get_current_datetime_kasese":
                            # Execute the function and get the result
                            tool_result = get_current_datetime_kasese(**function_args)
                            st.write(f"DEBUG: Tool result: {tool_result}") # Debugging tool results
                            # Send the tool result back to the model
                            response_from_tool = st.session_state.chat_session.send_message(
                                genai.types.ToolResponse(
                                    tool_code=tool_call.function,
                                    text=tool_result # Pass the result as text
                                ),
                                stream=True
                            )
                            # Stream the model's response based on the tool result
                            for tool_chunk in response_from_tool:
                                if tool_chunk.text:
                                    full_response_content += tool_chunk.text
                                    yield tool_chunk.text
                        else:
                            yield f"Error: WiseBuddy tried to use an unknown tool: {function_name}"
            return # Exit after successful response generation

        except genai.types.BlockedPromptException as e:
            st.error("WiseBuddy detected potentially harmful content. Please try rephrasing your query.")
            st.exception(e)
            yield "I cannot respond to that query as it might violate safety guidelines. Please try asking something else."
            return
        except Exception as e:
            if attempt < max_retries - 1:
                st.warning(f"API call failed, retrying in {delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)
                delay *= 2 # Exponential backoff
            else:
                st.error(f"WiseBuddy encountered an error: {e}. Please try again later.")
                st.exception(e)
                yield "Oops! WiseBuddy encountered an issue and couldn't respond. Please try again."
            return # Exit after all retries exhausted

# --- Streamlit UI ---
st.set_page_config(page_title="WiseBuddy - Your AI Chat Assistant", page_icon="💡", layout="centered")
st.title("💡 WiseBuddy")
st.markdown("Your intelligent AI chat assistant, powered by Gemini 1.5 Flash.")

# --- Dark Mode Toggle ---
# Check if dark mode is active (requires Streamlit 1.18.0+)
# Streamlit 1.25.0+ has a better way with st.config.get_option('theme.base')
# For broader compatibility, we'll stick to CSS for now.
# Users can still set their Streamlit theme to dark in settings if they want.
# This simple toggle changes background for a 'darker' feel in custom elements.
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

col1, col2 = st.columns([1, 4])
with col1:
    if st.button("Toggle Dark Mode 🌙" if not st.session_state.dark_mode else "Toggle Light Mode ☀️"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.experimental_rerun() # Rerun to apply theme changes

# Custom CSS for a cleaner look (optional)
bg_color = "#f0f2f6" if not st.session_state.dark_mode else "#1e1e1e" # Light grey or dark grey
text_color = "#333333" if not st.session_state.dark_mode else "#f0f0f0" # Dark text or light text
user_bubble_bg = "#e0f7fa" if not st.session_state.dark_mode else "#2a4247" # Light blue or darker blue
model_bubble_bg = "#f0f0f0" if not st.session_state.dark_mode else "#333333" # Light grey or darker grey

st.markdown(f"""
<style>
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}
    .st-chat-message-user {{
        background-color: {user_bubble_bg};
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 8px;
        color: {text_color};
    }}
    .st-chat-message-model {{
        background-color: {model_bubble_bg};
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 8px;
        color: {text_color};
    }}
    .stButton>button {{
        width: 100%;
        background-color: #4CAF50; /* Green */
        color: white;
        border-radius: 10px;
        padding: 10px;
        border: none;
    }}
    .stButton>button:hover {{
        background-color: #45a049;
    }}
    /* Adjust input field appearance */
    .stTextInput>div>div>input {{
        border-radius: 10px;
        padding: 10px;
        background-color: {model_bubble_bg}; /* Match model bubble for consistency */
        color: {text_color};
        border: 1px solid #ccc; /* Add a subtle border */
    }}
    /* Specific styles for Streamlit chat elements */
    [data-testid="stChatMessage"] {{
        padding: 0.5rem 1rem;
        margin-bottom: 0.5rem;
    }}
    [data-testid="stVerticalBlock"] div:has(div.element-container) {{
        gap: 0.5rem;
    }}
</style>
""", unsafe_allow_html=True)

# --- New Chat Button ---
with col2:
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
if prompt := st.chat_input("Ask WiseBuddy anything...", key="chat_input"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("model"):
        with st.status("WiseBuddy is thinking...", expanded=False) as status_box:
            status_box.write("Connecting to Gemini...")
            # Use st.write_stream to display the response as it streams
            # This captures all streamed content and displays it.
            placeholder = st.empty()
            full_response_container = []

            for text_chunk in process_gemini_response(prompt):
                full_response_container.append(text_chunk)
                placeholder.markdown("".join(full_response_container) + "▌") # Add blinking cursor effect
            
            final_response = "".join(full_response_container)
            placeholder.markdown(final_response) # Display final response without cursor

            # Update status box based on response content (simple check)
            if "Oops!" not in final_response and "cannot respond" not in final_response and "Error" not in final_response:
                 status_box.update(label="WiseBuddy replied!", state="complete", expanded=False)
            else:
                 status_box.update(label="WiseBuddy encountered an issue.", state="error", expanded=False)

    # Add final model response to chat history
    st.session_state.messages.append({"role": "model", "content": final_response})

