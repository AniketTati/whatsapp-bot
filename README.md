# WhatsApp AI Bot

A WhatsApp bot that uses Ollama for AI-powered responses. The bot maintains conversation history and can be configured for different users with personalized tones and personas.

## Features

- WhatsApp integration using whatsapp-web.js
- AI responses using Ollama
- Conversation history tracking
- User-specific configurations
- Periodic message sending
- Safety guardrails for responses

## Prerequisites

- Node.js
- Python 3
- Chrome/Chromium browser
- Ollama installed and running

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd whatsapp-bot
```

2. Install Node.js dependencies:
```bash
npm install
```

3. Set up Python environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install requests
```

4. Configure users in `user_config.json`:
```json
{
    "users": [
        {
            "phone": "your-phone-number",
            "tone": "friendly",
            "persona": "You are a helpful assistant."
        }
    ]
}
```

5. Make sure Ollama is running with the Mistral model:
```bash
ollama run mistral
```

## Usage

1. Start the bot:
```bash
npm run dev
```

2. Scan the QR code with WhatsApp to authenticate

## Project Structure

- `index.js` - Main WhatsApp bot code
- `llm_bot.py` - Python AI integration with Ollama
- `user_config.json` - User configurations
- `whatsapp_history.db` - SQLite database for chat history

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request 