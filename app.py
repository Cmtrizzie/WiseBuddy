import streamlit as st
import random
import uuid
import datetime
import re

# --- Initialize Session State for Multiple Chats ---
# This dictionary stores all chat sessions, identified by a unique UUID.
# Each session contains its title, messages, timestamp, and archive status.
if 'chat_sessions' not in st.session_state:
    st.session_state['chat_sessions'] = {}
    # The ID of the currently active chat session.
    st.session_state['active_chat'] = None
    # Stores the current search query for filtering chats.
    st.session_state['search_query'] = ""
    # Used to pre-fill the input box, e.g., from a suggestion click.
    st.session_state['pre_fill_input'] = ""
    # Controls the visibility of archived chats in the sidebar.
    st.session_state['archived_chats_visible'] = False
    # Stores the current text in the input field before submission.
    st.session_state['current_input'] = ""
    # Tracks whether the sidebar is collapsed or expanded.
    st.session_state['sidebar_collapsed'] = False

# --- Helper Functions for Chat Management ---
def new_chat():
    """
    Creates a new chat session, assigns a unique ID, and sets it as active.
    Resets pre-fill and current input for the new chat.
    """
    chat_id = str(uuid.uuid4())
    # CORRECTED: Changed 'st.session_session_state' to 'st.session_state'
    st.session_state['chat_sessions'][chat_id] = {
        'title': f'New Chat {len(st.session_state["chat_sessions"]) + 1}',
        'messages': [],
        'timestamp': datetime.datetime.now().isoformat(),
        'archived': False
    }
    st.session_state['active_chat'] = chat_id
    st.session_state['pre_fill_input'] = ""
    st.session_state['current_input'] = ""

def generate_chat_title(user_input):
    """
    Generates a concise and meaningful title for a chat based on the first user input.
    Takes the first sentence and limits it to the first 5 words.
    """
    first_sentence = re.split(r'[.!?]', user_input)[0].strip()
    words = first_sentence.split()[:5]
    return ' '.join(words) + ("..." if len(first_sentence) > 15 else "")

# --- Streamlit Page Configuration ---
# Sets the page layout to wide, sidebar initially expanded, and defines the page title.
st.set_page_config(layout="wide", initial_sidebar_state="expanded", page_title="Professional Assistant")

# --- Enhanced CSS for Professional Styling ---
# Applies custom CSS to style the Streamlit application for a professional look.
# Uses CSS variables for easy theme customization.
st.markdown(f"""
<style>
    :root {{
        --sidebar-bg: #202123;
        --main-bg: #343541;
        --input-bg: #40414f;
        --border-color: #444654;
        --text-primary: #ececf1;
        --text-secondary: #8e8ea0;
        --accent: #10a37f;
        --user-bubble: #007bff; /* A professional blue for user messages */
        --bot-bubble: #444654; /* A dark grey for bot messages */
        --sidebar-actual-width: {'0px' if st.session_state.sidebar_collapsed else '260px'};
    }}
    
    html, body, .stApp {{
        margin: 0;
        padding: 0;
        height: 100%;
        background-color: var(--main-bg);
        color: var(--text-primary);
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, sans-serif;
        transition: all 0.3s ease;
    }}
    
    .stApp {{
        display: flex;
        flex-direction: row;
        height: 100vh;
    }}

    /* Streamlit's native sidebar container styling */
    [data-testid="stSidebar"] {{
        width: var(--sidebar-actual-width) !important;
        background-color: var(--sidebar-bg);
        padding-top: 10px;
        display: flex;
        flex-direction: column;
        transition: width 0.3s ease;
        overflow: hidden; /* Hide content when collapsed */
        position: relative;
        box-shadow: 2px 0 10px rgba(0,0,0,0.2);
        z-index: 100;
    }}
    
    /* Streamlit's main content area container styling */
    [data-testid="stAppViewContainer"] {{
        margin-left: var(--sidebar-actual-width) !important;
        transition: margin-left 0.3s ease;
    }}

    /* Content wrapper inside the sidebar to handle its own scrolling */
    .sidebar-content-wrapper {{
        flex-grow: 1; /* Allows content to take available space */
        overflow-y: auto; /* Enables scrolling for sidebar content */
        padding: 10px 15px;
        display: {'none' if st.session_state.sidebar_collapsed else 'block'};
        opacity: {'0' if st.session_state.sidebar_collapsed else '1'};
        transition: opacity 0.3s ease;
    }}
    
    .sidebar-header {{
        margin-bottom: 15px;
        padding-top: 15px;
    }}
    
    .new-chat-btn button {{ /* Target the actual button inside Streamlit's div */
        background-color: var(--main-bg);
        color: var(--text-primary);
        border: 1px solid var(--border-color);
        width: 100%;
        padding: 10px 15px;
        border-radius: 5px;
        font-weight: 500;
        transition: all 0.2s ease;
        text-align: center;
        cursor: pointer;
    }}
    
    .new-chat-btn button:hover {{
        background-color: var(--border-color);
        transform: translateY(-1px);
    }}
    
    .sidebar-search input {{
        background-color: var(--main-bg) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 5px !important;
        padding: 8px 12px !important;
        width: 100%;
        font-size: 0.9em;
    }}
    
    .section-title {{
        color: var(--text-secondary);
        font-size: 0.85em;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin: 20px 0 10px 0;
    }}
    
    .sidebar-chat-list button {{ /* Target the actual button inside Streamlit's div */
        background-color: var(--main-bg);
        color: var(--text-primary);
        border: none;
        padding: 10px 12px;
        margin-bottom: 6px;
        border-radius: 6px;
        cursor: pointer;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        font-size: 0.9em;
        position: relative;
        width: 100%; /* Ensure buttons fill container */
        text-align: left; /* Align text to left */
    }}
    
    .sidebar-chat-list button:hover {{
        background-color: var(--border-color);
        transform: translateX(2px);
    }}
    
    /* Specific styling for the active chat button */
    .sidebar-chat-list button.active-chat-button {{
        background-color: var(--border-color);
        border-left: 3px solid var(--accent);
        padding-left: 9px; /* Adjust padding due to border */
    }}
    
    .chat-item-title {{
        flex-grow: 1;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        padding-right: 25px;
    }}
    
    .sidebar-footer {{
        padding: 15px 0;
        border-top: 1px solid var(--border-color);
        color: var(--text-secondary);
        font-size: 0.9em;
        margin-top: auto;
        text-align: center; /* Center footer content */
    }}
    
    .user-profile {{
        display: flex;
        align-items: center;
        gap: 10px;
        justify-content: center; /* Center profile content */
    }}
    
    .user-avatar {{
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background-color: var(--accent);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
    }}
    
    /* Main Content Area */
    .main-header {{
        background-color: var(--main-bg);
        padding: 15px 25px;
        border-bottom: 1px solid var(--border-color);
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: sticky;
        top: 0;
        z-index: 50;
    }}

    .expand-sidebar-btn button {{
        background-color: var(--input-bg);
        color: var(--text-primary);
        border: 1px solid var(--border-color);
        padding: 8px 15px;
        border-radius: 5px;
        font-weight: 500;
        transition: all 0.2s ease;
        cursor: pointer;
        font-size: 1.1em;
    }}

    .expand-sidebar-btn button:hover {{
        background-color: var(--border-color);
    }}
    
    .chat-title-display {{
        font-size: 1.2em;
        font-weight: 500;
        flex-grow: 1; /* Allows title to take available space */
        text-align: center; /* Center the chat title */
    }}
    
    .get-plus-btn button {{
        background-color: var(--accent) !important;
        color: white !important;
        border: none !important;
        padding: 8px 20px !important;
        border-radius: 20px !important;
        font-weight: 500 !important;
        transition: background-color 0.2s ease !important;
    }}
    
    .get-plus-btn button:hover {{
        background-color: #0d8a6e !important;
    }}
    
    .chat-messages-container {{
        flex-grow: 1;
        overflow-y: auto;
        padding: 25px;
        padding-bottom: 120px; /* Space for fixed input area */
        display: flex;
        flex-direction: column;
    }}
    
    .message-row {{
        display: flex;
        width: 100%;
        max-width: 800px;
        margin: 0 auto 15px auto;
    }}
    
    .user-bubble, .bot-bubble {{
        max-width: 85%;
        padding: 15px 20px;
        border-radius: 18px;
        word-wrap: break-word;
        font-size: 1em;
        line-height: 1.6;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }}
    
    .user-bubble {{
        background-color: var(--user-bubble);
        margin-left: auto;
        border-bottom-right-radius: 5px; /* Sharpen one corner for user */
    }}
    
    .bot-bubble {{
        background-color: var(--bot-bubble);
        margin-right: auto;
        border-bottom-left-radius: 5px; /* Sharpen one corner for bot */
    }}
    
    /* Welcome Screen */
    .welcome-screen {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        flex-grow: 1;
        padding: 20px;
        text-align: center;
        color: var(--text-secondary);
        max-width: 800px;
        margin: 0 auto;
    }}
    
    .welcome-title {{
        font-size: 2.2em;
        margin-bottom: 40px;
        color: var(--text-primary);
        font-weight: 600;
        background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    
    .suggestion-list {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); /* Responsive grid */
        gap: 20px;
        width: 100%;
        text-align: left;
    }}
    
    .suggestion-item button {{ /* Target the actual button */
        display: flex;
        align-items: center;
        gap: 15px;
        padding: 18px 20px;
        background-color: rgba(64, 65, 79, 0.5);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        cursor: pointer;
        transition: all 0.2s ease;
        width: 100%; /* Ensure button fills container */
        text-align: left;
    }}
    
    .suggestion-item button:hover {{
        background-color: rgba(68, 70, 84, 0.8);
        transform: translateY(-3px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }}
    
    .suggestion-icon {{
        font-size: 1.8em;
        background: rgba(16, 163, 127, 0.15);
        width: 50px;
        height: 50px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--accent); /* Icon color from accent */
    }}
    
    .suggestion-text {{
        font-size: 1.1em;
        font-weight: 500;
        color: var(--text-primary);
    }}
    
    /* Input Area */
    .input-area-container {{
        position: fixed;
        bottom: 0;
        left: var(--sidebar-actual-width); /* Adjusts with sidebar collapse */
        right: 0;
        background: var(--main-bg);
        padding: 20px 0;
        border-top: 1px solid var(--border-color);
        display: flex;
        justify-content: center;
        transition: left 0.3s ease;
        z-index: 40;
    }}
    
    .input-wrapper {{
        width: 100%;
        max-width: 800px;
        padding: 0 25px;
    }}
    
    .input-group {{
        display: flex;
        align-items: center;
        background-color: var(--input-bg);
        border-radius: 25px;
        padding: 8px 20px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }}
    
    .input-group .stTextInput > div > div > input {{
        background: transparent !important;
        color: var(--text-primary) !important;
        border: none !important;
        padding: 14px 10px !important;
        font-size: 1.05em !important;
        box-shadow: none !important;
        width: 100%;
    }}
    
    .input-group .stTextInput > div > div > input::placeholder {{
        color: var(--text-secondary) !important;
    }}
    
    .send-btn button {{ /* Target the actual button */
        background: var(--accent) !important;
        color: white !important;
        border: none !important;
        padding: 10px 20px !important;
        border-radius: 20px !important;
        font-weight: 500 !important;
        transition: background-color 0.2s ease !important;
    }}
    
    .send-btn button:hover {{
        background: #0d8a6e !important;
    }}
    
    /* Hide Streamlit default elements */
    #MainMenu, header, footer, .stDeployButton, [data-testid="stToolbar"] {{
        display: none !important;
    }}
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {{
        width: 8px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: var(--main-bg);
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: var(--border-color);
        border-radius: 4px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: var(--text-secondary);
    }}
</style>
""", unsafe_allow_html=True)

# Initialize chats if no active chat exists (first load)
if not st.session_state.get('active_chat'):
    new_chat()

# --- Sidebar (Collapsible Side Navigation) ---
with st.sidebar:
    # Conditionally render the collapse button
    if not st.session_state.sidebar_collapsed:
        # Using a simple button to collapse the sidebar
        if st.button("Collapse Sidebar ❮", key="collapse_sidebar_btn", use_container_width=True):
            st.session_state.sidebar_collapsed = True
            st.experimental_rerun()

    # Content wrapper for the sidebar, only visible when not collapsed
    st.markdown("<div class='sidebar-content-wrapper'>", unsafe_allow_html=True)
    if not st.session_state.sidebar_collapsed:
        # New Chat button
        st.markdown("<div class='sidebar-header new-chat-btn'>", unsafe_allow_html=True)
        if st.button("+ New Chat", key="new_chat_btn_sidebar", use_container_width=True):
            new_chat()
            st.experimental_rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        # Search functionality
        st.session_state['search_query'] = st.text_input(
            "",
            value=st.session_state['search_query'],
            placeholder="Search chats...",
            key="chat_search_input",
            label_visibility="collapsed"
        )

        # Chats section
        st.markdown("<div class='section-title'>CHATS</div>", unsafe_allow_html=True)
        st.markdown("<div class='sidebar-chat-list'>", unsafe_allow_html=True)

        # Display active chats, filtered by search query
        for chat_id, chat_data in st.session_state['chat_sessions'].items():
            if not chat_data['archived'] and \
               st.session_state['search_query'].lower() in chat_data['title'].lower():
                is_active = (chat_id == st.session_state['active_chat'])
                
                # Use st.button with HTML to allow custom styling via script
                if st.button(
                    f"<div class='chat-item-title'>{chat_data['title']}</div>",
                    key=f"chat_{chat_id}",
                    use_container_width=True,
                    unsafe_allow_html=True,
                    help=f"Open chat: {chat_data['title']}"
                ):
                    st.session_state['active_chat'] = chat_id
                    st.session_state['current_input'] = ""
                    st.experimental_rerun()
                # Apply the active class to the button element using JavaScript after rendering
                if is_active:
                    st.markdown(f"""
                        <script>
                            const activeBtn = window.parent.document.querySelector('button[key="chat_{chat_id}"]');
                            if (activeBtn) {{
                                activeBtn.classList.add('active-chat-button');
                            }}
                        </script>
                    """, unsafe_allow_html=True)

        # Archive toggle
        if st.button("🗄️ Show Archived Chats" if not st.session_state['archived_chats_visible'] else "🗄️ Hide Archived Chats", 
                     key="archive_toggle", use_container_width=True):
            st.session_state['archived_chats_visible'] = not st.session_state['archived_chats_visible']
            st.experimental_rerun()

        # Archived chats section
        if st.session_state['archived_chats_visible']:
            archived_exists = False
            for chat_id, chat_data in st.session_state['chat_sessions'].items():
                if chat_data['archived'] and \
                   st.session_state['search_query'].lower() in chat_data['title'].lower():
                    if not archived_exists:
                        st.markdown("<div class='section-title'>ARCHIVED CHATS</div>", unsafe_allow_html=True)
                        archived_exists = True
                    
                    if st.button(chat_data['title'], key=f"archived_{chat_id}", use_container_width=True):
                        st.session_state['active_chat'] = chat_id
                        st.session_state['current_input'] = ""
                        st.experimental_rerun()

        st.markdown("</div>", unsafe_allow_html=True)  # End sidebar-chat-list
        
        # Sidebar Footer
        st.markdown("<div class='sidebar-footer'>", unsafe_allow_html=True)
        st.markdown("<div class='user-profile'>", unsafe_allow_html=True)
        st.markdown("<div class='user-avatar'>U</div>", unsafe_allow_html=True)
        st.markdown("<div><strong>Professional Account</strong><br>Business Plan</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)  # End sidebar-content-wrapper

# --- Main Chat Area ---
active_chat_id = st.session_state['active_chat']
if active_chat_id in st.session_state['chat_sessions']:
    active_chat_data = st.session_state['chat_sessions'][active_chat_id]
else:
    # If for some reason the active chat ID is invalid, create a new one.
    new_chat()
    active_chat_id = st.session_state['active_chat']
    active_chat_data = st.session_state['chat_sessions'][active_chat_id]

# Main Header
st.markdown("<div class='main-header'>", unsafe_allow_html=True)
# Conditionally render the expand sidebar button
if st.session_state.sidebar_collapsed:
    col_expand_btn, col_title, col_upgrade_btn = st.columns([0.1, 0.8, 0.1])
    with col_expand_btn:
        if st.button("❯", key="expand_sidebar_btn", help="Expand sidebar", use_container_width=True):
            st.session_state.sidebar_collapsed = False
            st.experimental_rerun()
        # Apply custom styling for the expand button using JavaScript after rendering
        st.markdown(f"""
            <script>
                const expandBtn = window.parent.document.querySelector('button[key="expand_sidebar_btn"]');
                if (expandBtn) {{
                    expandBtn.classList.add('expand-sidebar-btn');
                }}
            </script>
        """, unsafe_allow_html=True)
    with col_title:
        st.markdown(f"<div class='chat-title-display'>{active_chat_data['title']}</div>", unsafe_allow_html=True)
    with col_upgrade_btn:
        st.button("✨ Upgrade to Pro", key="get_plus_btn", help="Get advanced features", use_container_width=True)
else:
    # If sidebar is open, just show title and upgrade button
    col_title, col_upgrade_btn = st.columns([0.9, 0.1])
    with col_title:
        st.markdown(f"<div class='chat-title-display'>{active_chat_data['title']}</div>", unsafe_allow_html=True)
    with col_upgrade_btn:
        st.button("✨ Upgrade to Pro", key="get_plus_btn", help="Get advanced features", use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True) # End main-header

# Chat messages display area
st.markdown("<div class='chat-messages-container'>", unsafe_allow_html=True)

if not active_chat_data['messages']:
    # Professional welcome screen when no messages in current chat
    st.markdown("<div class='welcome-screen'>", unsafe_allow_html=True)
    st.markdown("<div class='welcome-title'>How can I assist you today?</div>", unsafe_allow_html=True)
    st.markdown("<div class='suggestion-list'>", unsafe_allow_html=True)
    
    # Professional suggestions for initial interaction
    suggestions = [
        ("💡", "Create a strategic plan"),
        ("📊", "Analyze business metrics"),
        ("📝", "Draft professional documents"),
        ("🔍", "Research industry trends")
    ]
    
    # Display suggestions in a grid-like layout
    # Using columns for layout within the Streamlit app
    cols = st.columns(2)
    for i, (icon, text) in enumerate(suggestions):
        with cols[i % 2]: # Distribute suggestions across two columns
            # Wrap the button in a div to apply custom styling
            st.markdown(f"<div class='suggestion-item'>", unsafe_allow_html=True)
            if st.button(
                f"<span class='suggestion-icon'>{icon}</span> <span class='suggestion-text'>{text}</span>", 
                key=f"suggest_{text.replace(' ', '_')}",
                use_container_width=True,
                unsafe_allow_html=True,
                help=f"Start: {text}"
            ):
                st.session_state['pre_fill_input'] = f"{text}: "
                st.experimental_rerun()
            st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True) # End suggestion-list, welcome-screen
else:
    # Display actual chat messages
    for msg in active_chat_data['messages']:
        if msg['role'] == 'user':
            st.markdown(f"<div class='message-row'><div class='user-bubble'>{msg['content']}</div></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='message-row'><div class='bot-bubble'>{msg['content']}</div></div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)  # End chat-messages-container

# --- Input Area (Fixed at the bottom) ---
st.markdown("<div class='input-area-container'>", unsafe_allow_html=True)
st.markdown("<div class='input-wrapper'>", unsafe_allow_html=True)

# Initialize input value from pre-fill or current input state
input_value = st.session_state.get('pre_fill_input', '') or st.session_state.get('current_input', '')

# Create columns for the text input and send button
input_col, send_col = st.columns([0.9, 0.1])

with input_col:
    # Text input field for user messages
    user_input = st.text_input(
        "",
        value=input_value,
        placeholder="Message your professional assistant...",
        key='user_input_field',
        label_visibility="collapsed" # Hides the default Streamlit label
    )
    # Update current input state whenever the text input changes
    st.session_state['current_input'] = user_input
    
    # Clear pre-fill after its value has been used to populate the input box
    if st.session_state.get('pre_fill_input'):
        st.session_state['pre_fill_input'] = ""

with send_col:
    # Send button for submitting the message
    # Add a class for custom styling
    send_clicked = st.button("Send", key="send_btn", help="Send message", use_container_width=True)
    # Apply custom styling for the send button using JavaScript after rendering
    st.markdown(f"""
        <script>
            const sendBtn = window.parent.document.querySelector('button[key="send_btn"]');
            if (sendBtn) {{
                sendBtn.classList.add('send-btn');
            }}
        </script>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)  # End input-wrapper
st.markdown("</div>", unsafe_allow_html=True)  # End input-area-container

# Handle message submission logic
# This block executes when the send button is clicked and there's valid input.
if send_clicked and st.session_state['current_input'].strip():
    user_input = st.session_state['current_input'].strip()
    
    # Add user message to the active chat's message list
    active_chat_data['messages'].append({'role': 'user', 'content': user_input})
    
    # Auto-generate chat title if it's a new chat (default title)
    if active_chat_data['title'].startswith('New Chat'):
        active_chat_data['title'] = generate_chat_title(user_input)
    
    # Define a list of professional AI responses for demonstration
    responses = [
        "Based on your query about **{}**, here's a professional analysis:",
        "Regarding **{}**, I recommend the following strategic approach:",
        "After reviewing **{}**, I've compiled these insights:",
        "For **{}**, consider these professional recommendations:"
    ]
    
    # Extract the first meaningful keyword from user input for dynamic response
    keywords = re.findall(r'\b(\w{4,})\b', user_input) # Finds words with 4 or more characters
    keyword = keywords[0] if keywords else "your query" # Default if no keyword found
    
    # Select a random professional response and format it with the extracted keyword
    ai_response = random.choice(responses).format(keyword)
    # Add the AI's response to the active chat's message list
    active_chat_data['messages'].append({'role': 'assistant', 'content': ai_response})
    
    # Clear the input field and pre-fill state after message submission
    st.session_state['current_input'] = ""
    st.session_state['pre_fill_input'] = ""
    
    # Rerun the app to update the UI with new messages
    st.experimental_rerun()

