import streamlit as st
import google.generativeai as genai
import os
import time
from pathlib import Path
from datetime import datetime
import pytz # For time zone handling

# Import the specific types needed for function declaration
# Ensure you have google-generativeai installed, as these come with it.
# This import is crucial for correctly defining tools.
from google.generativeai.types import FunctionDeclaration, Tool as GenaiTool # Alias Tool to avoid conflict with st.Tool if it ever existed


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

# Correct way to declare the function as a tool for the Gemini model
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
        "required": [] # timezone is optional
    }
)

# Create a list of tools for the model
# We wrap the FunctionDeclaration in a GenaiTool object
tools = [
    GenaiTool(function_declarations=[get_current_datetime_kasese_tool])
]


# --- API Key Management ---
# ... (rest of the API Key Management section remains unchanged) ...
GEMINI_API_KEY = None
try:
    GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")
except Exception:
    pass

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

# ... (rest of your app.py code remains the same, including session state, helper function, UI, etc.) ...
# The `process_gemini_response` function that calls `model.start_chat` and `send_message` remains the same,
# as it correctly handles tool_calls once they are properly declared.

