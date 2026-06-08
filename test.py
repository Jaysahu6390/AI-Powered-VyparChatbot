# test_memory.py — Verify multi-turn memory works correctly
from chatbot_core import create_chain, chat, get_chat_history
from config import get_system_prompt

chain = create_chain(get_system_prompt("kirana_store"))

# Test 1: Basic Hindi query
r1 = chat(chain, "Namaste! Aapke paas basmati chawal hai?")
print("Bot:", r1)

# Test 2: Follow-up (tests memory — bot should remember the conversation)
r2 = chat(chain, "Woh kitne ka hai per kilo?")
print("Bot:", r2)

# Test 3: Complaint handling
r3 = chat(chain, "Maine kal order kiya tha, abhi tak deliver nahi hua")
print("Bot:", r3)

# Test 4: Switch to English mid-conversation (multilingual test)
r4 = chat(chain, "What are your store timings?")
print("Bot:", r4)

# Inspect memory
print("\n--- Memory Contents ---")
for msg in get_chat_history(chain):
    print(f"{msg['role']}: {msg['content'][:60]}...")