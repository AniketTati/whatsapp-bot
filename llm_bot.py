import json
import sqlite3
import datetime
import sys
import requests
from functools import lru_cache

DB_PATH = "whatsapp_history.db"
CONFIG_PATH = "user_config.json"

# Cache user settings to avoid file reads
@lru_cache(maxsize=100)
def load_user_settings():
    with open(CONFIG_PATH, "r") as file:
        return json.load(file)["users"]

@lru_cache(maxsize=100)
def get_user_settings(phone):
    users = load_user_settings()
    for user in users:
        if user["phone"] == phone:
            return user["tone"], user["persona"]
    return "neutral", "You are a helpful assistant."

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT,
            message TEXT,
            timestamp TEXT
        )
    """)
    # Add index for faster queries
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_phone_timestamp ON messages(phone, timestamp)")
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def save_message(phone, message, timestamp):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (phone, message, timestamp) VALUES (?, ?, ?)", 
                   (phone, message, timestamp))
    conn.commit()
    conn.close()

def get_chat_history(phone, limit=3):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Get only last few messages for faster context
    cursor.execute("""
        SELECT message FROM messages 
        WHERE phone = ? 
        ORDER BY timestamp DESC 
        LIMIT ?
    """, (phone, limit))
    messages = [row[0] for row in cursor.fetchall()]
    conn.close()
    return list(reversed(messages))  # Return in chronological order

# Initialize Ollama client
OLLAMA_ENDPOINT = "http://localhost:11434/api/chat"
MODEL_NAME = "neural-chat"  # Faster model

# Performance options for faster responses
OLLAMA_OPTIONS = {
    "temperature": 0.7,
    "top_k": 40,
    "top_p": 0.9,
    "num_predict": 100,  # Limit response length
    "repeat_penalty": 1.1,
    "num_ctx": 512,  # Smaller context window for speed
    "num_thread": 4  # Use multiple threads
}

# Cache blocked words set for faster lookup
BLOCKED_WORDS = frozenset(["violence", "hate speech", "illegal", "scam", "threat"])

def is_safe_response(response):
    return not any(bad_word in response.lower() for bad_word in BLOCKED_WORDS)

def get_ai_response(phone, message):
    try:
        # Get minimal context - only last 3 messages
        chat_history = get_chat_history(phone, limit=3)
        tone, persona = get_user_settings(phone)

        # Build minimal prompt with personality
        context = "\n".join(chat_history) if chat_history else ""
        
        # Create a more natural system prompt that incorporates personality
        system_prompt = f"""You are a real person with the following personality: {persona}
Your communication style is {tone}. 
Important guidelines:
- Respond naturally like a real person, not an AI assistant
- Use casual language and contractions (I'm, you're, etc.)
- Show personality and emotion in your responses
- Keep responses concise but friendly
- Use appropriate emojis occasionally
- Don't use formal language or AI-like phrases
- If you're being friendly, use exclamation marks naturally
- Don't mention being an AI or assistant
- Don't use phrases like "I understand" or "I can help you with that"
- Be conversational and engaging"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]

        # Add context only if it exists, but frame it as previous conversation
        if context:
            messages.insert(1, {"role": "assistant", "content": f"Previous conversation:\n{context}"})

        # Get AI response with timeout
        response = requests.post(
            OLLAMA_ENDPOINT, 
            json={
                "model": MODEL_NAME,
                "messages": messages,
                "stream": False,
                "options": OLLAMA_OPTIONS
            },
            timeout=15  # Shorter timeout
        )
        response.raise_for_status()
        ai_response = response.json()["message"]["content"]

        if not is_safe_response(ai_response):
            return "I'm sorry, but I can't respond to that."

        # Save messages
        current_time = datetime.datetime.now().isoformat()
        save_message(phone, message, current_time)
        save_message(phone, ai_response, current_time)

        return ai_response

    except requests.exceptions.Timeout:
        # Silently retry once before giving up
        try:
            return get_ai_response(phone, message)
        except:
            return ""
    except Exception as e:
        print(f"Error calling Ollama: {e}", file=sys.stderr)
        return ""

# Initialize database
init_db()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 llm_bot.py <phone_number> <message>")
        sys.exit(1)
    
    try:
        response = get_ai_response(sys.argv[1], sys.argv[2])
        print(response)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
