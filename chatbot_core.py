# chatbot_core.py — The LangChain + Groq + Memory engine

from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
from langchain.chains.conversation.base import ConversationChain
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
import os
from dotenv import load_dotenv

load_dotenv()

# ─── CONCEPT 1: LLM Initialization ───────────────────────────────────────────
def create_llm():
    """
    Groq gives you LLaMA-3 70B for FREE.
    temperature=0.7: balanced creativity vs accuracy
    max_tokens=512: enough for shop replies, saves API quota
    """
    return ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama-3.1-8b-instant",
        temperature=0.7,
        max_tokens=512,
    )

# ─── CONCEPT 2: Conversation Memory ─────────────────────────────────────────
def create_memory():
    """
    ConversationBufferMemory stores the FULL chat history.
    return_messages=True: returns LangChain message objects (needed for ChatModels)
    memory_key="chat_history": this key must match the placeholder in the prompt
    
    What happens without memory:
    - User: "mere order ka status kya hai?"
    - User: "woh 2 kg aata tha"  ← Bot won't know what order they mean!
    
    What happens WITH memory:
    - Bot remembers the entire conversation thread
    """
    return ConversationBufferMemory(
        return_messages=True,
        memory_key="chat_history",
        human_prefix="Customer",
        ai_prefix="Assistant"
    )

# ─── CONCEPT 3: Multilingual Prompt Template ────────────────────────────────
def create_prompt(system_prompt: str):
    """
    ChatPromptTemplate structures our messages for ChatModels.
    
    Three parts:
    1. SystemMessagePromptTemplate: WHO the bot is (injected once)
    2. MessagesPlaceholder: WHERE the history goes (auto-filled by memory)
    3. HumanMessagePromptTemplate: The current user message
    """
    return ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),  # ← memory plugs in here
        HumanMessagePromptTemplate.from_template("{input}"),
    ])

# ─── CONCEPT 4: Building the Chain ──────────────────────────────────────────
def create_chain(system_prompt: str):
    """
    ConversationChain = LLM + Memory + Prompt, connected together.
    
    Data flow per message:
    user_input 
      → prompt_template fills {input} 
      → memory fills {chat_history}
      → system_prompt sets the persona
      → full prompt sent to Groq LLaMA-3
      → response returned and saved to memory
    """
    llm = create_llm()
    memory = create_memory()
    prompt = create_prompt(system_prompt)
    
    chain = ConversationChain(
        llm=llm,
        memory=memory,
        prompt=prompt,
        verbose=False  # Set True to see full prompt in terminal (great for debugging!)
    )
    return chain

# ─── CONCEPT 5: Chat Function ────────────────────────────────────────────────
def chat(chain: ConversationChain, user_message: str) -> str:
    """
    Sends a message and gets a response.
    Memory is automatically updated inside the chain.
    """
    try:
        response = chain.predict(input=user_message)
        return response
    except Exception as e:
        print(f"FULL ERROR: {e}")  # Add this line
        if "rate_limit" in str(e).lower():
            return "Thodi der baad try karein..."
        if "api_key" in str(e).lower() or "authentication" in str(e).lower():
            return "API key missing or invalid. Check your .env file."
        return f"Error: {str(e)}"  # Show actual error instead of hiding it

# ─── BONUS: Memory Inspector (for debugging/learning) ───────────────────────
def get_chat_history(chain: ConversationChain) -> list:
    """Returns the raw memory buffer — great for understanding what LangChain stores."""
    messages = chain.memory.chat_memory.messages
    history = []
    for msg in messages:
        role = "Customer" if msg.__class__.__name__ == "HumanMessage" else "Bot"
        history.append({"role": role, "content": msg.content})
    return history