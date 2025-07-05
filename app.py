import streamlit as st
import random
import uuid
import datetime
import re

# --- Initialize Session State for Multiple Chats ---
if 'chat_sessions' not in st.session_state:
    st.session_state['chat_sessions'] = {}
    st.session_state['active_chat'] = None
    st.session_state['search_query'] = ""
    st.session_state['pre_fill_input'] = ""
    st.session_state['archived_chats_visible'] = False
    st.session_state['current_input'] = ""
    st.session_state['sidebar_collapsed'] = False  # Track sidebar state

# --- Helper Functions for Chat Management ---
def new_chat():
    chat_id = str(uuid.uuid4())
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
    """Generate a meaningful title from user input"""
    first_sentence = re.split(r'[.!?]', user_input)[0].strip()
    words = first_sentence.split()[:5]
    return ' '.join(words) + ("..." if len(first_sentence) > 15 else "")

# --- Streamlit Page Configuration ---
st.set_page_config(layout="wide", initial_sidebar_state="expanded", page_title="Professional Assistant")

# --- Enhanced CSS for Professional Styling ---
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
        --user-bubble: #007bff;
        --bot-bubble: #444654;
        --sidebar-width: {'0px' if st.session_state.sidebar_collapsed else '260px'};
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

    /* Slidebar Styling */
    .stSidebar {{
        width: var(--sidebar-width) !important;
        background-color: var(--sidebar-bg);
        padding-top: 10px;
        display: flex;
        flex-direction: column;
        transition: width 0.3s ease;
        overflow: hidden;
        position: relative;
        box-shadow: 2px 0 10px rgba(0,0,0,0.2);
        z-index: 100;
    }}
    
    .sidebar-toggle {{
        position: absolute;
        top: 12px;
        right: 12px;
        background: var(--main-bg);
        border: none;
        color: var(--text-primary);
        border-radius: 50%;
        width: 30px;
        height: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        z-index: 100;
        font-size: 1.2em;
    }}
    
    .sidebar-content {{
        width: 260px;
        padding: 10px 15px;
        display: {'none' if st.session_state.sidebar_collapsed else 'block'};
        opacity: {'0' if st.session_state.sidebar_collapsed else '1'};
        transition: opacity 0.3s ease;
    }}
    
    .sidebar-header {{
        margin-bottom: 15px;
        padding-top: 15px;
    }}
    
    .new-chat-btn {{
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
    
    .new-chat-btn:hover {{
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
    
    .sidebar-chat-list {{
        max-height: calc(100vh - 250px);
        overflow-y: auto;
        padding-right: 5px;
    }}
    
    .sidebar-chat-item {{
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
    }}
    
    .sidebar-chat-item:hover {{
        background-color: var(--border-color);
        transform: translateX(2px);
    }}
    
    .sidebar-chat-item.active-chat {{
        background-color: var(--border-color);
        border-left: 3px solid var(--accent);
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
    }}
    
    .user-profile {{
        display: flex;
        align-items: center;
        gap: 10px;
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
    
    .chat-title-display {{
        font-size: 1.2em;
        font-weight: 500;
    }}
    
    .get-plus-btn {{
        background-color: var(--accent) !important;
        color: white !important;
        border: none !important;
        padding: 8px 20px !important;
        border-radius: 20px !important;
        font-weight: 500 !important;
        transition: background-color 0.2s ease !important;
    }}
    
    .get-plus-btn:hover {{
        background-color: #0d8a6e !important;
    }}
    
    .chat-messages-container {{
        flex-grow: 1;
        overflow-y: auto;
        padding: 25px;
        padding-bottom: 120px;
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
        border-bottom-right-radius: 5px;
    }}
    
    .bot-bubble {{
        background-color: var(--bot-bubble);
        margin-right: auto;
        border-bottom-left-radius: 5px;
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
        grid-template-columns: repeat(2, 1fr);
        gap: 20px;
        width: 100%;
        text-align: left;
    }}
    
    .suggestion-item {{
        display: flex;
        align-items: center;
        gap: 15px;
        padding: 18px 20px;
        background-color: rgba(64, 65, 79, 0.5);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        cursor: pointer;
        transition: all 0.2s ease;
    }}
    
    .suggestion-item:hover {{
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
    }}
    
    .suggestion-text {{
        font-size: 1.1em;
        font-weight: 500;
    }}
    
    /* Input Area */
    .input-area-container {{
        position: fixed;
        bottom: 0;
        left: var(--sidebar-width);
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
    
    .send-btn {{
        background: var(--accent) !important;
        color: white !important;
        border: none !important;
        padding: 10px 20px !important;
        border-radius: 20px !important;
        font-weight: 500 !important;
        transition: background-color 0.2s ease !important;
    }}
    
    .send-btn:hover {{
        background: #0d8a6e !important;
    }}
    
    /* Hide Streamlit default elements */
    #MainMenu, header, footer, .stDeployButton {{
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

# Initialize chats if needed
if not st.session_state.get('chat_sessions'):
    new_chat()

# --- Slidebar (Collapsible Side Navigation) ---
with st.sidebar:
    # Toggle button for slidebar
    toggle_icon = "❮" if not st.session_state.sidebar_collapsed else "❯"
    if st.button(toggle_icon, key="sidebar_toggle", help="Toggle sidebar"):
        st.session_state.sidebar_collapsed = not st.session_state.sidebar_collapsed
        st.experimental_rerun()
    
    # Slidebar content container
    st.markdown("<div class='sidebar-content'>", unsafe_allow_html=True)
    
    # New Chat button
    st.markdown("<div class='sidebar-header'>", unsafe_allow_html=True)
    if st.button("+ New Chat", key="new_chat_btn", use_container_width=True):
        new_chat()
        st.experimental_rerun()
    st.markdown("</div>")

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

    # Display active chats
    for chat_id, chat_data in st.session_state['chat_sessions'].items():
        if not chat_data['archived']:
            is_active = (chat_id == st.session_state['active_chat'])
            if st.button(
                chat_data['title'], 
                key=f"chat_{chat_id}",
                use_container_width=True
            ):
                st.session_state['active_chat'] = chat_id
                st.session_state['current_input'] = ""
                st.experimental_rerun()

    # Archive toggle
    if st.button("🗄️ Show Archived Chats" if not st.session_state['archived_chats_visible'] else "🗄️ Hide Archived Chats", 
                 key="archive_toggle", use_container_width=True):
        st.session_state['archived_chats_visible'] = not st.session_state['archived_chats_visible']
        st.experimental_rerun()

    # Archived chats section
    if st.session_state['archived_chats_visible']:
        archived_exists = False
        for chat_id, chat_data in st.session_state['chat_sessions'].items():
            if chat_data['archived']:
                if not archived_exists:
                    st.markdown("<div class='section-title'>ARCHIVED CHATS</div>", unsafe_allow_html=True)
                    archived_exists = True
                
                if st.button(chat_data['title'], key=f"archived_{chat_id}", use_container_width=True):
                    st.session_state['active_chat'] = chat_id
                    st.session_state['current_input'] = ""
                    st.experimental_rerun()

    st.markdown("</div>")  # End sidebar-chat-list
    
    # Slidebar Footer
    st.markdown("<div class='sidebar-footer'>", unsafe_allow_html=True)
    st.markdown("<div class='user-profile'>", unsafe_allow_html=True)
    st.markdown("<div class='user-avatar'>U</div>", unsafe_allow_html=True)
    st.markdown("<div><strong>Professional Account</strong><br>Business Plan</div>", unsafe_allow_html=True)
    st.markdown("</div>")
    st.markdown("</div>")
    
    st.markdown("</div>")  # End sidebar-content

# --- Main Chat Area ---
active_chat_id = st.session_state['active_chat']
if active_chat_id in st.session_state['chat_sessions']:
    active_chat_data = st.session_state['chat_sessions'][active_chat_id]
else:
    # Create new chat if active chat doesn't exist
    new_chat()
    active_chat_id = st.session_state['active_chat']
    active_chat_data = st.session_state['chat_sessions'][active_chat_id]

# Main Header
st.markdown("<div class='main-header'>", unsafe_allow_html=True)
st.markdown(f"<div class='chat-title-display'>{active_chat_data['title']}</div>", unsafe_allow_html=True)
st.button("✨ Upgrade to Pro", key="get_plus_btn", help="Get advanced features")
st.markdown("</div>")

# Chat messages display area
st.markdown("<div class='chat-messages-container'>", unsafe_allow_html=True)

if not active_chat_data['messages']:
    # Professional welcome screen
    st.markdown("<div class='welcome-screen'>", unsafe_allow_html=True)
    st.markdown("<div class='welcome-title'>How can I assist you today?</div>", unsafe_allow_html=True)
    st.markdown("<div class='suggestion-list'>", unsafe_allow_html=True)
    
    # Professional suggestions
    suggestions = [
        ("💡", "Create a strategic plan"),
        ("📊", "Analyze business metrics"),
        ("📝", "Draft professional documents"),
        ("🔍", "Research industry trends")
    ]
    
    for icon, text in suggestions:
        # Use columns for better layout
        col1, col2 = st.columns([1, 1])
        with col1 if icon == "💡" or icon == "📊" else col2:
            if st.button(
                f"**{text}**", 
                key=f"suggest_{text.replace(' ', '_')}",
                use_container_width=True,
                help=f"Start: {text}"
            ):
                st.session_state['pre_fill_input'] = f"{text}: "
                st.experimental_rerun()
    
    st.markdown("</div></div>", unsafe_allow_html=True)
else:
    # Display actual messages
    for msg in active_chat_data['messages']:
        if msg['role'] == 'user':
            st.markdown(f"<div class='message-row'><div class='user-bubble'>{msg['content']}</div></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='message-row'><div class='bot-bubble'>{msg['content']}</div></div>", unsafe_allow_html=True)

st.markdown("</div>")  # End chat-messages-container

# --- Input Area ---
st.markdown("<div class='input-area-container'>", unsafe_allow_html=True)
st.markdown("<div class='input-wrapper'>", unsafe_allow_html=True)

# Initialize input value
input_value = st.session_state.get('pre_fill_input', '') or st.session_state.get('current_input', '')

# Create columns for layout
input_col, send_col = st.columns([0.9, 0.1])

with input_col:
    # Text input field
    user_input = st.text_input(
        "",
        value=input_value,
        placeholder="Message your professional assistant...",
        key='user_input_field',
        label_visibility="collapsed"
    )
    # Update current input state
    st.session_state['current_input'] = user_input
    
    # Clear pre-fill after use
    if st.session_state.get('pre_fill_input'):
        st.session_state['pre_fill_input'] = ""

with send_col:
    # Send button
    send_clicked = st.button("Send", key="send_btn", help="Send message", use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)  # End input-wrapper
st.markdown("</div>", unsafe_allow_html=True)  # End input-area-container

# Handle message submission
if send_clicked and st.session_state['current_input'].strip():
    user_input = st.session_state['current_input'].strip()
    
    # Add user message
    active_chat_data['messages'].append({'role': 'user', 'content': user_input})
    
    # Auto-generate title if it's a new chat
    if active_chat_data['title'].startswith('New Chat'):
        active_chat_data['title'] = generate_chat_title(user_input)
    
    # Professional AI responses
    responses = [
        "Based on your query about **{}**, here's a professional analysis...",
        "Regarding **{}**, I recommend the following strategic approach:",
        "After reviewing **{}**, I've compiled these insights:",
        "For **{}**, consider these professional recommendations:"
    ]
    
    # Extract first keyword from user input
    keywords = re.findall(r'\b(\w{4,})\b', user_input)
    keyword = keywords[0] if keywords else "your query"
    
    ai_response = random.choice(responses).format(keyword)
    active_chat_data['messages'].append({'role': 'assistant', 'content': ai_response})
    
    # Clear input after submission
    st.session_state['current_input'] = ""
    st.session_state['pre_fill_input'] = ""
    
    st.experimental_rerun()
