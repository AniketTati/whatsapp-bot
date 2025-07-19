# WhatsApp AI Bot

A WhatsApp bot that uses Ollama for AI-powered responses. The bot maintains conversation history and can be configured for different users with personalized tones and personas.

## Features

- WhatsApp integration using whatsapp-web.js
- AI responses using Ollama with multiple model support
- Conversation history tracking with SQLite
- User-specific configurations and personas
- Cross-platform Chrome/Chromium detection
- Safety guardrails for responses
- Configurable periodic messages
- Input validation and error handling
- REST API for external integration

## Prerequisites

- Node.js (v16 or higher)
- Python 3.7+
- Chrome, Chromium, or compatible browser
- Ollama installed and running with a supported model

## Quick Start

Run the setup script to install dependencies and validate the setup:

```bash
./setup.sh
```

## Manual Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd whatsapp-bot
```

2. Install Node.js dependencies:
```bash
PUPPETEER_SKIP_DOWNLOAD=true npm install
```

3. Install Python dependencies:
```bash
pip3 install -r requirements.txt
```

4. Install and start Ollama:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama run mistral
```

5. Configure users in `user_config.json`:
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

## Usage

1. Start the bot:
```bash
npm start
```

2. Scan the QR code with WhatsApp to authenticate

3. The bot will respond to messages from configured users

## Testing

Run the validation tests to ensure everything is working:

```bash
python3 test_validation.py
```

## Project Structure

- `index.js` - Main WhatsApp bot with cross-platform support
- `llm_bot.py` - Python AI integration with Ollama and database handling
- `api_server.py` - FastAPI server for REST API access
- `user_config.json` - User configurations (copy from user_config_example.json)
- `requirements.txt` - Python dependencies
- `test_validation.py` - Validation tests for code correctness
- `setup.sh` - Automated setup script
- `whatsapp_history.db` - SQLite database for chat history (auto-created)

## API Endpoints

The bot includes a FastAPI server with the following endpoints:

- `POST /chat` - Send a message and get AI response
- `POST /sync_history` - Sync chat history from external sources
- `GET /health` - Health check endpoint

Start the API server:
```bash
python3 api_server.py
```

## Troubleshooting

### Common Issues

1. **Puppeteer Chrome not found**: The bot automatically detects Chrome/Chromium on different platforms
2. **Ollama connection failed**: Ensure Ollama is running on localhost:11434
3. **Module not found**: Run `pip3 install -r requirements.txt`
4. **Database locked**: Restart the bot if SQLite database gets locked

### Supported Ollama Models

The bot supports these models in order of preference:
- neural-chat
- mistral  
- llama2
- codellama

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request 