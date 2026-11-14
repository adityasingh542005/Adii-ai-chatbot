
import os
import uuid
import textwrap
import streamlit as st

from langchain_groq import ChatGroq
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    SystemMessage
)

# =====================================================
# 1. PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Adii AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# 2. CUSTOM CSS
# =====================================================

css = """
<style>

.stApp {
    background: #0b0d14;
    color: #f1f2f8;
}

.block-container {
    max-width: 1100px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

[data-testid="stSidebar"] {
    background: #11131d;
    border-right: 1px solid #25283a;
}

[data-testid="stSidebar"] .block-container {
    padding-top: 2rem;
}

.brand {
    font-size: 30px;
    font-weight: 800;
    background: linear-gradient(90deg, #b69aff, #68a5ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.brand-sub {
    color: #85899e;
    font-size: 11px;
    letter-spacing: 2px;
}

.hero {
    text-align: center;
    padding-top: 65px;
    padding-bottom: 40px;
}

.hero-icon {
    font-size: 45px;
    color: #b69aff;
}

.hero-title {
    font-size: 53px;
    font-weight: 800;
    letter-spacing: -2px;
    background: linear-gradient(90deg, #c4a7ff, #72a9ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-subtitle {
    color: #999caf;
    font-size: 16px;
    margin-top: 12px;
    line-height: 1.7;
}

.section-heading {
    color: #e9e8f5;
    font-size: 19px;
    font-weight: 650;
    margin-bottom: 15px;
}

.stButton > button {
    background: #191b29;
    color: #eeeeF7;
    border: 1px solid #303349;
    border-radius: 12px;
    min-height: 45px;
    transition: 0.2s ease;
}

.stButton > button:hover {
    background: #29243d;
    border-color: #a78bfa;
    color: white;
}

[data-testid="stChatMessage"] {
    background: #151827;
    border: 1px solid #282d42;
    border-radius: 16px;
    padding: 17px;
    margin-bottom: 15px;
}

[data-testid="stChatInput"] {
    background: #151827;
    border: 1px solid #474563;
    border-radius: 17px;
}

[data-testid="stChatInput"] textarea {
    color: white;
}

hr {
    border-color: #292d40;
}

#MainMenu,
footer {
    visibility: hidden;
}

</style>
"""

st.markdown(
    textwrap.dedent(css),
    unsafe_allow_html=True
)

# =====================================================
# 3. API KEY CONFIGURATION
# =====================================================

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        api_key = None

if not api_key:
    st.error("Groq API key is missing.")
    st.stop()

# =====================================================
# 4. LOAD GROQ MODEL
# =====================================================

@st.cache_resource
def load_model(key, temperature):

    return ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=temperature,
        api_key=key
    )

# =====================================================
# 5. SESSION STATE INITIALIZATION
# =====================================================

if "chats" not in st.session_state:

    st.session_state.chats = {}

if "active_chat_id" not in st.session_state:

    st.session_state.active_chat_id = None

if "pending_prompt" not in st.session_state:

    st.session_state.pending_prompt = None

# Create initial conversation if needed

if not st.session_state.chats:

    first_id = str(uuid.uuid4())

    st.session_state.chats[first_id] = {
        "title": "New Chat",
        "messages": []
    }

    st.session_state.active_chat_id = first_id

# Ensure active conversation exists

if st.session_state.active_chat_id not in st.session_state.chats:

    st.session_state.active_chat_id = next(
        iter(st.session_state.chats)
    )

# =====================================================
# 6. CHAT MANAGEMENT FUNCTIONS
# =====================================================

def create_chat():

    chat_id = str(uuid.uuid4())

    st.session_state.chats[chat_id] = {
        "title": "New Chat",
        "messages": []
    }

    st.session_state.active_chat_id = chat_id


def delete_chat(chat_id):

    if chat_id in st.session_state.chats:

        del st.session_state.chats[chat_id]

    if not st.session_state.chats:

        create_chat()

    elif st.session_state.active_chat_id == chat_id:

        st.session_state.active_chat_id = next(
            iter(st.session_state.chats)
        )


# =====================================================
# 7. SIDEBAR
# =====================================================

with st.sidebar:

    st.markdown(
        '<div class="brand">✦ Adii AI</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="brand-sub">YOUR INTELLIGENT COMPANION</div>',
        unsafe_allow_html=True
    )

    st.write("")

    # New Chat

    if st.button("＋  New Chat", use_container_width=True):

        create_chat()

        st.session_state.pending_prompt = None

        st.rerun()

    st.divider()

    # Chat History

    st.markdown("### 💬 Chat History")

    chat_items = list(st.session_state.chats.items())

    if not chat_items:

        st.caption("No conversations yet.")

    for chat_id, chat in reversed(chat_items):

        col1, col2 = st.columns([5, 1])

        with col1:

            is_active = (
                chat_id == st.session_state.active_chat_id
            )

            label = (
                "● " + chat["title"]
                if is_active
                else chat["title"]
            )

            if st.button(
                label,
                key=f"open_{chat_id}",
                use_container_width=True
            ):

                st.session_state.active_chat_id = chat_id

                st.session_state.pending_prompt = None

                st.rerun()

        with col2:

            if st.button(
                "×",
                key=f"delete_{chat_id}",
                help="Delete conversation"
            ):

                delete_chat(chat_id)

                st.rerun()

    st.divider()

    # Settings

    st.markdown("### ⚙️ Settings")

    temperature = st.slider(
        "AI Creativity",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1
    )

    response_style = st.selectbox(
        "Response Style",
        [
            "Balanced",
            "Simple English",
            "Professional",
            "Detailed"
        ]
    )

    st.caption("MODEL: GPT-OSS 120B")

    st.caption("POWERED BY GROQ")

    st.caption("FRAMEWORK: LANGCHAIN")

    st.divider()

    # Current conversation actions

    active_chat = st.session_state.chats[
        st.session_state.active_chat_id
    ]

    if active_chat["messages"]:

        st.markdown("### 📁 Chat Actions")

        conversation_text = ""

        for message in active_chat["messages"]:

            role = message["role"].upper()

            conversation_text += (
                f"{role}:\n{message['content']}\n\n"
            )

        st.download_button(
            "⬇ Download Conversation",
            data=conversation_text,
            file_name="adii_ai_conversation.txt",
            mime="text/plain",
            use_container_width=True
        )

        if st.button(
            "🗑 Clear Current Chat",
            use_container_width=True
        ):

            active_chat["messages"] = []

            active_chat["title"] = "New Chat"

            st.rerun()

    st.divider()

    # About

    st.markdown("### ✨ About Adii AI")

    st.caption(
        "Your intelligent companion for learning, "
        "coding, exploring and creating."
    )

    st.divider()

    st.caption("Developed by Aditya")

    st.caption("Adii AI • Version 3.0")


# =====================================================
# 8. LOAD MODEL USING CURRENT SETTINGS
# =====================================================

llm = load_model(api_key, temperature)

# =====================================================
# 9. GET ACTIVE CHAT
# =====================================================

active_chat = st.session_state.chats[
    st.session_state.active_chat_id
]

# =====================================================
# 10. WELCOME SCREEN
# =====================================================

if not active_chat["messages"]:

    hero_html = """
<div class="hero">
    <div class="hero-icon">✦</div>
    <div class="hero-title">Meet Adii AI</div>
    <div class="hero-subtitle">
        Your intelligent companion for learning,<br>
        coding and creativity.
    </div>
</div>
"""

    st.markdown(
        textwrap.dedent(hero_html),
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-heading">'
        '✨ What would you like to explore?'
        '</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "💻 Coding Assistant\n\nProgramming and debugging",
            use_container_width=True
        ):

            st.session_state.pending_prompt = (
                "Help me with programming and debugging."
            )

            st.rerun()

        if st.button(
            "🧠 Learn AI & ML\n\nUnderstand artificial intelligence",
            use_container_width=True
        ):

            st.session_state.pending_prompt = (
                "Teach me artificial intelligence and machine learning."
            )

            st.rerun()

    with col2:

        if st.button(
            "📚 Study Assistant\n\nLearn difficult topics simply",
            use_container_width=True
        ):

            st.session_state.pending_prompt = (
                "Help me study and understand difficult topics."
            )

            st.rerun()

        if st.button(
            "🚀 Project Ideas\n\nDiscover interesting projects",
            use_container_width=True
        ):

            st.session_state.pending_prompt = (
                "Suggest unique AI and software project ideas."
            )

            st.rerun()


# =====================================================
# 11. DISPLAY CHAT HISTORY
# =====================================================

for message in active_chat["messages"]:

    if message["role"] == "user":

        avatar = "👤"

    else:

        avatar = "🤖"

    with st.chat_message(
        message["role"],
        avatar=avatar
    ):

        st.markdown(message["content"])


# =====================================================
# 12. CHAT INPUT
# =====================================================

prompt = st.chat_input("Message Adii AI...")

if prompt is None and st.session_state.pending_prompt:

    prompt = st.session_state.pending_prompt

    st.session_state.pending_prompt = None


# =====================================================
# 13. PROCESS USER MESSAGE
# =====================================================

if prompt:

    # Generate chat title

    if active_chat["title"] == "New Chat":

        title = prompt.strip().replace("\n", " ")

        if len(title) > 32:

            title = title[:32].rsplit(" ", 1)[0] + "..."

        active_chat["title"] = title or "New Chat"

    # Save user message

    active_chat["messages"].append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user", avatar="👤"):

        st.markdown(prompt)

    # Response styles

    style_instructions = {

        "Balanced": (
            "Give clear, balanced and helpful answers."
        ),

        "Simple English": (
            "Explain everything in very simple English "
            "with easy examples."
        ),

        "Professional": (
            "Respond professionally and formally."
        ),

        "Detailed": (
            "Give detailed explanations, examples and "
            "step-by-step reasoning where appropriate."
        )
    }

    # Prepare LangChain messages

    chat_messages = [

        SystemMessage(
            content=(
                "You are Adii AI, a friendly, intelligent "
                "and helpful AI assistant. "
                + style_instructions[response_style]
            )
        )

    ]

    for message in active_chat["messages"]:

        if message["role"] == "user":

            chat_messages.append(
                HumanMessage(content=message["content"])
            )

        else:

            chat_messages.append(
                AIMessage(content=message["content"])
            )

    # Generate AI response

    with st.chat_message("assistant", avatar="🤖"):

        with st.spinner("Adii AI is thinking..."):

            try:

                response = llm.invoke(chat_messages)

                answer = response.content

                st.markdown(answer)

                active_chat["messages"].append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception as e:

                st.error(
                    f"Something went wrong: {e}"
                )

                active_chat["messages"].pop()

