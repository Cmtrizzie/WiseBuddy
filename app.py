import streamlit as st
import google.generativeai as genai
import os
import time
from pathlib import Path
from datetime import datetime
import pytz # For time zone handling

# Import the specific types needed for function declaration
from google.generativeai.types import FunctionDeclaration, Tool as GenaiTool

st.sidebar.write("DEBUG: 1. Imports and initial setup complete.")
print("DEBUG: 1. Imports and initial setup complete.")

# --- Configuration & Environment Setup ---
BASE_DIR = Path(__file__).resolve().parent
MODEL_NAME = "gemini-1.5-flash"
SYSTEM_INSTRUCTION = """
You are WiseBuddy, a friendly, empathetic, and highly knowledgeable AI assistant.
Your primary goal is to provide concise, accurate, and relevant information.
Maintain a positive, approachable, and slightly encouraging tone.
Always strive to be helpful and provide clear, easy-to-understand explanations.
If you don't know the answer, politely state that you cannot provide information on that specific topic or suggest where the user might find it.
Prioritize user safety and ensure all responses are ethical and respectful.
You can also use tools to get real-world information if needed.
"""
st.sidebar.write("DEBUG: 2. Configuration and System Instruction defined.")
print("DEBUG: 2. Configuration and System Instruction defined.")


# --- Tool Definitions (for Function Calling) ---
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

get_current_datetime_kasese_tool = FunctionDeclaration(
    name="get_current_datetime_kasese",
    description="Returns the current date and time in a specified timezone. Defaults to Kasese, Western Region, Uganda (Africa/Kampala).",
    parameters={
        "type": "object",
        "properties": {
            "timezone": {
                "type": "string",
                "description": "The IANA timezone string, e.g., 'America/New_York' or 'Europe/London'. Defaults to 'Africa/Kampala'."
            }
        },
        "required": []
    }
)

tools = [
    GenaiTool(function_declarations=[get_current_datetime_kasese_tool])
]
st.sidebar.write("DEBUG: 3. Tool definitions complete.")
print("DEBUG: 3. Tool definitions complete.")


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
else:
    st.sidebar.write("DEBUG: 4. API Key found and processed.")
    print("DEBUG: 4. API Key found and processed.")

genai.configure(api_key=GEMINI_API_KEY)
st.sidebar.write("DEBUG: 5. Gemini API configured.")
print("DEBUG: 5. Gemini API configured.")


# --- Model Initialization ---
model = genai.GenerativeModel(MODEL_NAME, system_instruction=SYSTEM_INSTRUCTION, tools=tools)
st.sidebar.write("DEBUG: 6. GenerativeModel initialized.")
print("DEBUG: 6. GenerativeModel initialized.")


# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []
st.sidebar.write(f"DEBUG: 7. Session state 'messages' initialized. Current messages count: {len(st.session_state.messages)}")
print(f"DEBUG: 7. Session state 'messages' initialized. Current messages count: {len(st.session_state.messages)}")


if "chat_session" not in st.session_state:
    st.session_state.chat_session = None # Initialize as None, create on first message or new chat
st.sidebar.write("DEBUG: 8. Session state 'chat_session' initialized.")
print("DEBUG: 8. Session state 'chat_session' initialized.")

if st.session_state.chat_session is None or not st.session_state.messages:
    st.session_state.chat_session = model.start_chat(history=st.session_state.messages)
    st.sidebar.write("DEBUG: 9. New chat session started/re-initialized.")
    print("DEBUG: 9. New chat session started/re-initialized.")


# --- Helper Function for Gemini API Call with Streaming & Function Calling ---
def process_gemini_response(prompt_text, max_retries=3, delay=1):
    st.sidebar.write("DEBUG: 10. Entering process_gemini_response function.")
    print("DEBUG: 10. Entering process_gemini_response function.")
    for attempt in range(max_retries):
        try:
            st.sidebar.write(f"DEBUG: 10.1 Attempt {attempt+1} to send message to Gemini.")
            print(f"DEBUG: 10.1 Attempt {attempt+1} to send message to Gemini.")
            response_generator = st.session_state.chat_session.send_message(prompt_text, stream=True)

            full_response_content = ""
            for chunk in response_generator:
                if chunk.text:
                    full_response_content += chunk.text
                    yield chunk.text
                if chunk.tool_calls:
                    st.sidebar.write(f"DEBUG: 10.2 Model requested tool call.")
                    print(f"DEBUG: 10.2 Model requested tool call.")
                    for tool_call in chunk.tool_calls:
                        function_name = tool_call.function.name
                        function_args = tool_call.function.args

                        st.sidebar.write(f"DEBUG: 10.3 Model called function: {function_name} with args: {function_args}")
                        print(f"DEBUG: 10.3 Model called function: {function_name} with args: {function_args}")
                        if function_name == "get_current_datetime_kasese":
                            tool_result = get_current_datetime_kasese(**function_args)
                            st.sidebar.write(f"DEBUG: 10.4 Tool result: {tool_result}")
                            print(f"DEBUG: 10.4 Tool result: {tool_result}")
                            response_from_tool = st.session_state.chat_session.send_message(
                                genai.types.ToolResponse(
                                    tool_code=tool_call.function,
                                    text=tool_result
                                ),
                                stream=True
                            )
                            for tool_chunk in response_from_tool:
                                if tool_chunk.text:
                                    full_response_content += tool_chunk.text
                                    yield tool_chunk.text
                        else:
                            yield f"Error: WiseBuddy tried to use an unknown tool: {function_name}"
            st.sidebar.write("DEBUG: 10.5 Response generation complete.")
            print("DEBUG: 10.5 Response generation complete.")
            return

        except genai.types.BlockedPromptException as e:
            st.error("WiseBuddy detected potentially harmful content. Please try rephrasing your query.")
            st.exception(e)
            yield "I cannot respond to that query as it might violate safety guidelines. Please try asking something else."
            return
        except Exception as e:
            if attempt < max_retries - 1:
                st.warning(f"API call failed, retrying in {delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)
                delay *= 2
            else:
                st.error(f"WiseBuddy encountered an error: {e}. Please try again later.")
                st.exception(e)
                yield "Oops! WiseBuddy encountered an issue and couldn't respond. Please try again."
            return
    st.sidebar.write("DEBUG: 10.6 Exiting process_gemini_response after retries.")
    print("DEBUG: 10.6 Exiting process_gemini_response after retries.")


# --- Streamlit UI ---
st.set_page_config(page_title="WiseBuddy - Your AI Chat Assistant", page_icon="💡", layout="centered")
st.title("💡 WiseBuddy")
st.markdown("Your intelligent AI chat assistant, powered by Gemini 1.5 Flash.")
st.sidebar.write("DEBUG: 11. Page config and initial title set.")
print("DEBUG: 11. Page config and initial title set.")


# --- Dark Mode Toggle ---
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

col1, col2 = st.columns([1, 4])
with col1:
    if st.button("Toggle Dark Mode 🌙" if not st.session_state.dark_mode else "Toggle Light Mode ☀️"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun() # CHANGED FROM st.experimental_rerun()
st.sidebar.write("DEBUG: 12. Dark mode toggle rendered.")
print("DEBUG: 12. Dark mode toggle rendered.")

# Custom CSS for a cleaner look
bg_color = "#f0f2f6" if not st.session_state.dark_mode else "#1e1e1e"
text_color = "#333333" if not st.session_state.dark_mode else "#f0f0f0"
user_bubble_bg = "#e0f7fa" if not st.session_state.dark_mode else "#2a4247"
model_bubble_bg = "#f0f0f0" if not st.session_state.dark_mode else "#333333"

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
        background-color: #4CAF50;
        color: white;
        border-radius: 10px;
        padding: 10px;
        border: none;
    }}
    .stButton>button:hover {{
        background-color: #45a049;
    }}
    .stTextInput>div>div>input {{
        border-radius: 10px;
        padding: 10px;
        background-color: {model_bubble_bg};
        color: {text_color};
        border: 1px solid #ccc;
    }}
    [data-testid="stChatMessage"] {{
        padding: 0.5rem 1rem;
        margin-bottom: 0.5rem;
    }}
    [data-testid="stVerticalBlock"] div:has(div.element-container) {{
        gap: 0.5rem;
    }}
</style>
""", unsafe_allow_html=True)
st.sidebar.write("DEBUG: 13. Custom CSS applied.")
print("DEBUG: 13. Custom CSS applied.")


# --- New Chat Button ---
with col2:
    if st.button("✨ Start a New Chat", help="Clear current conversation and start fresh"):
        st.session_state.messages = []
        st.session_state.chat_session = model.start_chat(history=[])
        st.rerun() # CHANGED FROM st.experimental_rerun()
st.sidebar.write("DEBUG: 14. New chat button rendered.")
print("DEBUG: 14. New chat button rendered.")


# Display existing chat messages from history
st.sidebar.write(f"DEBUG: 15. Starting to display {len(st.session_state.messages)} chat messages.")
print(f"DEBUG: 15. Starting to display {len(st.session_state.messages)} chat messages.")
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
st.sidebar.write("DEBUG: 16. Finished displaying chat messages.")
print("DEBUG: 16. Finished displaying chat messages.")


# --- User Input and Model Response Logic ---
# DEBUG: This entire section is commented out to isolate the problem.
# If the app renders now, the issue is within this block.
# If it's still blank, the issue is earlier in the script.

# st.sidebar.write("DEBUG: 17. Checking for user input (st.chat_input).")
# print("DEBUG: 17. Checking for user input (st.chat_input).")
# if prompt := st.chat_input("Ask WiseBuddy anything...", key="chat_input"):
#     st.sidebar.write("DEBUG: 18. User input received.")
#     print("DEBUG: 18. User input received.")
#     st.session_state.messages.append({"role": "user", "content": prompt})
#     with st.chat_message("user"):
#         st.markdown(prompt)
#     st.sidebar.write("DEBUG: 19. User message added and displayed.")
#     print("DEBUG: 19. User message added and displayed.")

#     with st.chat_message("model"):
#         with st.status("WiseBuddy is thinking...", expanded=False) as status_box:
#             status_box.write("Connecting to Gemini...")
#             st.sidebar.write("DEBUG: 20. Calling process_gemini_response.")
#             print("DEBUG: 20. Calling process_gemini_response.")
#             placeholder = st.empty()
#             full_response_container = []

#             for text_chunk in process_gemini_response(prompt):
#                 full_response_container.append(text_chunk)
#                 placeholder.markdown("".join(full_response_container) + "▌")

#             final_response = "".join(full_response_container)
#             placeholder.markdown(final_response)

#             if "Oops!" not in final_response and "cannot respond" not in final_response and "Error" not in final_response:
#                  status_box.update(label="WiseBuddy replied!", state="complete", expanded=False)
#             else:
#                  status_box.update(label="WiseBuddy encountered an issue.", state="error", expanded=False)
#     st.sidebar.write("DEBUG: 21. Model response displayed and status updated.")
#     print("DEBUG: 21. Model response displayed and status updated.")

#     st.session_state.messages.append({"role": "model", "content": final_response})
#     st.sidebar.write("DEBUG: 22. Model response added to session state.")
#     print("DEBUG: 22. Model response added to session state.")

st.sidebar.write("DEBUG: 23. End of script execution (main loop).")
print("DEBUG: 23. End of script execution (main loop).")

