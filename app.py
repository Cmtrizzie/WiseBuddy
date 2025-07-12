import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# --- 1. Load Environment Variables (for API Key) ---
# This will load variables from a .env file if it exists.
# For deployment on Streamlit Community Cloud, use Streamlit Secrets.
load_dotenv()

# --- 2. Configure Gemini API Key ---
# Get the API key from environment variables or Streamlit Secrets.
# For local development, put GEMINI_API_KEY="YOUR_API_KEY" in a .env file.
# For Streamlit Cloud, add GEMINI_API_KEY to your app's secrets.
try:
    # Attempt to get from Streamlit Secrets first (for deployment)
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    # Fallback to environment variable (for local testing)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    st.error("Gemini API key not found. Please set GEMINI_API_KEY in your environment variables or Streamlit Secrets.")
    st.stop() # Stop the app if no API key is found

genai.configure(api_key=GEMINI_API_KEY)

# --- 3. Initialize Gemini Model ---
# We'll use the 'gemini-1.5-flash' model
MODEL_NAME = "gemini-1.5-flash"
model = genai.GenerativeModel(MODEL_NAME)

# --- 4. Initialize Chat History in Session State ---
# This is where we store the conversation to maintain context.
if "messages" not in st.session_state:
    st.session_state.messages = [] # Format: [{"role": "user", "content": "..."}] or {"role": "model", "content": "..."}]

# --- 5. Streamlit UI Structure ---
st.set_page_config(page_title="WiseBuddy - Your AI Chat Assistant", page_icon="💡")
st.title("💡 WiseBuddy")
st.markdown("Your intelligent AI chat assistant, powered by Gemini 1.5 Flash.")

# Optional: Add a 'Clear Chat' button in the sidebar
with st.sidebar:
    st.subheader("Options")
    if st.button("Clear Chat History", help="Start a new conversation"):
        st.session_state.messages = []
        st.experimental_rerun() # Rerun the app to clear display

# Display existing chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 6. Chat Logic (User Input and Model Response) ---
if prompt := st.chat_input("Ask WiseBuddy anything..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare conversation history for Gemini API
    # Gemini API expects alternating user/model roles.
    # Convert st.session_state.messages to the format expected by model.start_chat().
    # For a simple turn-by-turn chat, we can just pass the history as is.
    # For more complex scenarios, you might need to map roles or content.

    # Start a chat session with the model
    # Passing history ensures context is maintained for the model
    chat_session = model.start_chat(history=st.session_state.messages)

    with st.chat_message("model"):
        with st.spinner("WiseBuddy is thinking..."):
            try:
                # Send the user's prompt (which is already in chat_session.history implicitly)
                # and get the response from Gemini
                response = chat_session.send_message(prompt)
                full_response = response.text
                st.markdown(full_response)
            except Exception as e:
                st.error(f"An error occurred: {e}")
                full_response = "Oops! WiseBuddy encountered an issue. Please try again."

    # Add model response to chat history
    st.session_state.messages.append({"role": "model", "content": full_response})

