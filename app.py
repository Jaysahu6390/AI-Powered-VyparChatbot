# app.py — VyaparBot: Hindi-English Business Chatbot

import streamlit as st
from chatbot_core import create_chain, chat, get_chat_history
from config import BUSINESS_CONFIGS, get_system_prompt

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VyaparBot — Business Assistant",
    page_icon="🏪",
    layout="wide"
)

# ─── CUSTOM CSS (Kanpur/UP feel) ──────────────────────────────────────────────
st.markdown("""
<style>
    .stChatMessage { border-radius: 12px; }
    .main-header {
        background: linear-gradient(135deg, #FF6B35, #F7931E);
        padding: 1.5rem; border-radius: 12px;
        color: white; text-align: center; margin-bottom: 1.5rem;
    }
    .business-card {
    background: rgba(255, 107, 53, 0.15); border-left: 4px solid #FF6B35;
    padding: 0.8rem 1rem; border-radius: 8px;
    margin-bottom: 1rem; font-size: 0.85rem;
    color: inherit;
}
    .memory-badge {
        background: #e8f5e9; color: #2e7d32;
        padding: 2px 8px; border-radius: 12px; font-size: 0.75rem;
    }
</style>
""", unsafe_allow_html=True)

# ─── SIDEBAR: BUSINESS CONFIGURATION ─────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏪 Business Setup")
    st.markdown("*Apne business ke liye configure karein*")
    
    # Business type selector
    business_options = {
        "kirana_store": "🛒 Kirana / General Store",
        "coaching_centre": "📚 Coaching Centre",
        "medical_shop": "💊 Medical / Pharmacy"
    }
    
    selected_business = st.selectbox(
        "Business Type", 
        options=list(business_options.keys()),
        format_func=lambda x: business_options[x]
    )
    
    config = BUSINESS_CONFIGS[selected_business]
    
    # Show current config
    st.markdown(f"""
    <div class="business-card">
        <strong>{config['name']}</strong><br>
        📍 {config['location']}<br>
        🕐 {config['timing']}<br>
        🗣️ {config['language']}
    </div>
    """, unsafe_allow_html=True)
    
    # Custom business name override
    custom_name = st.text_input("Custom Business Name (optional)", 
                                 placeholder=config['name'])
    
    # Language preference
    lang_pref = st.radio(
        "Default Language",
        ["Auto-detect", "Hindi", "English", "Hinglish"],
        index=0
    )
    
    # Reset chat button
    if st.button("🔄 Reset Conversation", use_container_width=True):
        st.session_state.clear()
        st.rerun()
    
    # Memory inspector (for learning/debugging)
    if st.checkbox("🔍 Show Memory (Debug Mode)"):
        if "chain" in st.session_state and st.session_state.chain:
            history = get_chat_history(st.session_state.chain)
            st.json(history)
        else:
            st.info("Start chatting to see memory")
    
    st.markdown("---")
    st.markdown("**Powered by:**")
    st.markdown("🦙 Groq LLaMA-3 70B")
    st.markdown("🔗 LangChain ConversationChain")
    st.markdown("🤗 HuggingFace Spaces")

# ─── MAIN HEADER ─────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="main-header">
    <h1 style="margin:0; font-size:1.8rem">🏪 VyaparBot</h1>
    <p style="margin:0.3rem 0 0; opacity:0.9">
        {config['name']} · 24/7 Customer Support · Hindi & English
    </p>
</div>
""", unsafe_allow_html=True)

# ─── SESSION STATE INITIALIZATION ────────────────────────────────────────────
# This is how Streamlit maintains state across reruns
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chain" not in st.session_state or st.session_state.get("current_business") != selected_business:
    # Create a fresh LangChain chain when business changes
    system_prompt = get_system_prompt(selected_business)
    if lang_pref != "Auto-detect":
        system_prompt += f"\nIMPORTANT: Always respond in {lang_pref}."
    
    st.session_state.chain = create_chain(system_prompt)
    st.session_state.current_business = selected_business
    
    # Add welcome message
    welcome_messages = {
        "kirana_store": f"Namaste! 🙏 {config['name']} mein aapka swagat hai. Main aapki kya madad kar sakta hoon?",
        "coaching_centre": f"Hello! 👋 {config['name']} mein aapka swagat hai. Admission, fees, ya classes ke baare mein kuch poochna hai?",
        "medical_shop": f"Namaste! 💊 {config['name']} mein aapka swagat hai. Kaise help kar sakta hoon? (For emergencies, please call 108)"
    }
    
    if not st.session_state.messages:
        st.session_state.messages.append({
            "role": "assistant",
            "content": welcome_messages.get(selected_business, "Namaste! Kaise help kar sakta hoon?")
        })

# ─── CHAT DISPLAY ─────────────────────────────────────────────────────────────
# Show message count badge
if len(st.session_state.messages) > 1:
    turns = (len(st.session_state.messages) - 1) // 2
    st.markdown(f'<span class="memory-badge">💾 {turns} conversation turns in memory</span>', 
                unsafe_allow_html=True)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# ─── CHAT INPUT & RESPONSE ────────────────────────────────────────────────────
# Example prompts for user guidance
example_prompts = {
    "kirana_store": ["Kya aapke paas basmati chawal hai?", "Delivery kab hogi?", "Udhar milega?"],
    "coaching_centre": ["JEE ki fees kitni hai?", "Demo class kab hai?", "Class timings batao"],
    "medical_shop": ["Paracetamol available hai?", "Generic alternative kya hai?", "Home delivery hoti hai?"]
}

# Quick reply buttons
st.markdown("**Quick questions:**")
cols = st.columns(3)
for i, example in enumerate(example_prompts.get(selected_business, [])):
    if cols[i].button(example, key=f"example_{i}"):
        st.session_state.pending_message = example

user_input = st.chat_input("Apna sawaal yahan likhein... (Hindi ya English mein)")

# Handle both direct input and quick-reply button
if "pending_message" in st.session_state:
    user_input = st.session_state.pop("pending_message")

if user_input:
    # Add user message to display
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)
    
    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Soch raha hoon..."):
            response = chat(st.session_state.chain, user_input)
        st.write(response)
    
    # Save assistant response
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()