import streamlit as st
import uuid
import base64

# ----------------- PAGE CONFIG -----------------
st.set_page_config(
    page_title="My Assistant 🤖",
    page_icon=":robot_face:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://docs.streamlit.io',
        'Report a bug': "https://github.com/streamlit/streamlit/issues",
        'About': "# AI Research Assistant v1.0"
    }
)

# ----------------- SESSION STATE INIT -----------------
if "topics" not in st.session_state:
    st.session_state.topics = {}
    st.session_state.active_topic = None
    st.session_state.active_mode = "Research"
    st.session_state.expanded_files = True

# ----------------- FUNCTIONAL HELPERS -----------------
def create_topic(name):
    if not name.strip():
        st.error("Topic name cannot be empty!")
        return
        
    topic_id = str(uuid.uuid4())
    st.session_state.topics[topic_id] = {
        "name": name,
        "files": [],
        "summaries": {},
        "chat": [],
        "created": st.session_state.get('current_time', 'Unknown')
    }
    st.session_state.active_topic = topic_id
    st.success(f"Created topic: {name}")

def switch_topic(topic_id):
    st.session_state.active_topic = topic_id

def set_mode(mode):
    st.session_state.active_mode = mode
    st.experimental_rerun()

def delete_topic(topic_id):
    if topic_id in st.session_state.topics:
        name = st.session_state.topics[topic_id]["name"]
        del st.session_state.topics[topic_id]
        if st.session_state.active_topic == topic_id:
            st.session_state.active_topic = None
        st.success(f"Deleted topic: {name}")

def delete_file(topic_id, file_index):
    try:
        file_name = st.session_state.topics[topic_id]["files"][file_index].name
        st.session_state.topics[topic_id]["files"].pop(file_index)
        st.success(f"Removed: {file_name}")
    except IndexError:
        st.error("File index error")

# ----------------- SIDEBAR: TOPICS & NAV -----------------
with st.sidebar:
    st.title("📁 Topic Manager")
    
    # Topic creation section
    with st.expander("➕ Create New Topic", expanded=True):
        new_topic = st.text_input("Topic Name", key="new_topic", 
                                  placeholder="Enter topic name...")
        if st.button("Create", key="create_btn", use_container_width=True):
            create_topic(new_topic)
    
    st.markdown("---")
    st.subheader("Your Topics")
    
    # Topics list with management
    for tid, topic in st.session_state.topics.items():
        cols = st.columns([4, 1])
        active = tid == st.session_state.active_topic
        
        with cols[0]:
            if st.button(
                f"{'▶️' if active else '📌'} {topic['name']}",
                key=f"switch_{tid}",
                use_container_width=True,
                help=f"Switch to {topic['name']}"
            ):
                switch_topic(tid)
                
        with cols[1]:
            if st.button("🗑️", key=f"del_{tid}", help=f"Delete {topic['name']}"):
                delete_topic(tid)
    
    st.markdown("---")
    st.caption(f"Total topics: {len(st.session_state.topics)}")
    if st.button("Clear All Topics", type="secondary"):
        st.session_state.topics = {}
        st.session_state.active_topic = None
        st.success("All topics cleared!")

# ----------------- HEADER NAVIGATION -----------------
st.header("My Research Assistant", divider="rainbow")

# Mode selection
mode_cols = st.columns(4)
with mode_cols[0]:
    st.button("📚 Research Mode", 
              on_click=set_mode, args=("Research",),
              disabled=st.session_state.active_mode=="Research",
              use_container_width=True)
    
with mode_cols[1]:
    st.button("🛠️ Tools Mode", 
              on_click=set_mode, args=("Tools",),
              disabled=st.session_state.active_mode=="Tools",
              use_container_width=True)

# File uploader
with mode_cols[3]:
    uploaded_files = st.file_uploader(
        "Upload PDF(s)", 
        type="pdf", 
        accept_multiple_files=True,
        help="Upload research documents",
        label_visibility="collapsed"
    )

# Process new uploads
if uploaded_files and st.session_state.active_topic:
    current_files = [f.name for f in st.session_state.topics[st.session_state.active_topic]["files"]]
    new_files = [f for f in uploaded_files if f.name not in current_files]
    
    if new_files:
        st.session_state.topics[st.session_state.active_topic]["files"].extend(new_files)
        st.success(f"Added {len(new_files)} file(s) to current topic!")

# ----------------- MAIN PANEL -----------------
if not st.session_state.active_topic:
    st.info("👋 Welcome! Create your first topic to get started.")
    st.image("https://cdn.pixabay.com/photo/2017/01/31/00/09/artificial-intelligence-2022460_960_720.png", 
             caption="AI Research Assistant")
    st.stop()

# Get current topic
active_topic = st.session_state.topics[st.session_state.active_topic]
st.subheader(f"Current Topic: **{active_topic['name']}**")

# File management section - FIXED SYNTAX ERROR HERE
with st.expander(f"📁 Document Manager ({len(active_topic['files']}) files", 
                expanded=st.session_state.expanded_files):
    if active_topic["files"]:
        for i, f in enumerate(active_topic["files"]):
            cols = st.columns([1, 8, 1])
            cols[0].image("https://cdn-icons-png.flaticon.com/512/337/337946.png", width=30)
            cols[1].write(f"**{f.name}**")
            with cols[2]:
                if st.button("✖️", key=f"del_{i}", help=f"Remove {f.name}"):
                    delete_file(st.session_state.active_topic, i)
                    st.experimental_rerun()
    else:
        st.warning("No documents uploaded yet. Add PDFs to start researching!")

# Mode-specific content
st.markdown("---")
if st.session_state.active_mode == "Research":
    st.subheader("🔍 Research Assistant")
    
    # Simulated chat interface
    with st.chat_message("ai", avatar="🤖"):
        st.markdown(f"Hello! I'm ready to help with **{active_topic['name']}** research.")
        st.caption("Upload documents to get started")
    
    # Example research features
    research_cols = st.columns(3)
    with research_cols[0]:
        with st.container(border=True):
            st.markdown("### 📝 Document Summary")
            st.progress(30)
            st.caption("Upload documents to generate summaries")
            
    with research_cols[1]:
        with st.container(border=True):
            st.markdown("### ❓ Ask Questions")
            st.text_area("Ask about your documents...", height=100, key="research_question")
            st.button("Ask AI", disabled=not active_topic["files"], key="ask_ai_btn")
            
    with research_cols[2]:
        with st.container(border=True):
            st.markdown("### 🔍 Key Insights")
            st.caption("Key findings will appear here")
            st.image("https://cdn-icons-png.flaticon.com/512/3209/3209260.png", width=80)

elif st.session_state.active_mode == "Tools":
    st.subheader("🛠️ PDF Toolkit")
    
    # PDF tools section
    tool_cols = st.columns(3)
    
    with tool_cols[0]:
        with st.container(border=True, height=200):
            st.markdown("### 🔗 Merge PDFs")
            st.caption("Combine multiple documents")
            st.progress(0)
            st.button("Merge Files", disabled=len(active_topic["files"]) < 2, key="merge_btn")
    
    with tool_cols[1]:
        with st.container(border=True, height=200):
            st.markdown("### ✂️ Split PDF")
            st.caption("Extract specific pages")
            st.progress(0)
            st.button("Split Document", disabled=not active_topic["files"], key="split_btn")
    
    with tool_cols[2]:
        with st.container(border=True, height=200):
            st.markdown("### 🗜️ Compress PDF")
            st.caption("Reduce file size")
            st.progress(0)
            st.button("Compress Files", disabled=not active_topic["files"], key="compress_btn")

# ----------------- FOOTER -----------------
st.markdown("---")
footer_cols = st.columns([3, 1])
with footer_cols[0]:
    st.caption("My Assistant v1.1 • Created with 💙 by Trizzie & Maya")
with footer_cols[1]:
    st.caption(f"Active topic: {active_topic['name']} | Mode: {st.session_state.active_mode}")
