#!/bin/bash

echo "🚀 WhatsApp Bot Setup Script"
echo "============================"

# Check Node.js
if command -v node &> /dev/null; then
    echo "✅ Node.js found: $(node --version)"
else
    echo "❌ Node.js not found. Please install Node.js first."
    exit 1
fi

# Check Python
if command -v python3 &> /dev/null; then
    echo "✅ Python3 found: $(python3 --version)"
else
    echo "❌ Python3 not found. Please install Python3 first."
    exit 1
fi

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
PUPPETEER_SKIP_DOWNLOAD=true npm install

if [ $? -eq 0 ]; then
    echo "✅ Node.js dependencies installed"
else
    echo "❌ Failed to install Node.js dependencies"
    exit 1
fi

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip3 install -r requirements.txt --user

if [ $? -eq 0 ]; then
    echo "✅ Python dependencies installed"
else
    echo "❌ Failed to install Python dependencies"
    exit 1
fi

# Create user config if it doesn't exist
if [ ! -f "user_config.json" ]; then
    echo "📝 Creating user_config.json from example..."
    cp user_config_example.json user_config.json
    echo "⚠️  Please edit user_config.json with your phone numbers"
fi

# Run validation tests
echo "🧪 Running validation tests..."
python3 test_validation.py

echo ""
echo "🎉 Setup completed!"
echo ""
echo "Next steps:"
echo "1. Install and start Ollama with a supported model:"
echo "   curl -fsSL https://ollama.ai/install.sh | sh"
echo "   ollama run mistral"
echo ""
echo "2. Edit user_config.json with actual phone numbers"
echo ""
echo "3. Start the bot:"
echo "   npm start"
echo ""
echo "4. Scan the QR code with WhatsApp to authenticate"