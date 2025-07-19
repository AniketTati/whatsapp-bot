#!/usr/bin/env python3
"""
Basic functionality tests for WhatsApp bot components
"""

import sys
import os
import sqlite3
import json
import tempfile
import unittest
from unittest.mock import patch, MagicMock

# Add the current directory to path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import llm_bot
    import api_server
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

class TestLLMBot(unittest.TestCase):
    """Test cases for LLM bot functionality"""
    
    def setUp(self):
        """Set up test database"""
        self.test_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.test_db.close()
        
        # Temporarily replace DB_PATH
        self.original_db_path = llm_bot.DB_PATH
        llm_bot.DB_PATH = self.test_db.name
        
        # Initialize test database
        llm_bot.init_db()
    
    def tearDown(self):
        """Clean up test database"""
        llm_bot.DB_PATH = self.original_db_path
        os.unlink(self.test_db.name)
    
    def test_database_initialization(self):
        """Test that database is created correctly"""
        conn = sqlite3.connect(self.test_db.name)
        cursor = conn.cursor()
        
        # Check if messages table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='messages'")
        result = cursor.fetchone()
        self.assertIsNotNone(result)
        
        # Check table structure
        cursor.execute("PRAGMA table_info(messages)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        expected_columns = ['id', 'phone', 'message', 'timestamp']
        for col in expected_columns:
            self.assertIn(col, column_names)
        
        conn.close()
    
    def test_save_and_retrieve_message(self):
        """Test saving and retrieving messages"""
        test_phone = "1234567890"
        test_message = "Hello, test message!"
        test_timestamp = "2023-01-01T12:00:00"
        
        # Save message
        llm_bot.save_message(test_phone, test_message, test_timestamp)
        
        # Retrieve message
        history = llm_bot.get_chat_history(test_phone, limit=1)
        
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0], test_message)
    
    def test_user_settings(self):
        """Test user settings functionality"""
        # Test with default settings
        tone, persona = llm_bot.get_user_settings("nonexistent_phone")
        self.assertEqual(tone, "neutral")
        self.assertEqual(persona, "You are a helpful assistant.")
    
    def test_safety_filter(self):
        """Test safety response filter"""
        # Test safe response
        safe_response = "Hello! How are you today?"
        self.assertTrue(llm_bot.is_safe_response(safe_response))
        
        # Test unsafe response
        unsafe_response = "This contains violence and illegal content"
        self.assertFalse(llm_bot.is_safe_response(unsafe_response))
    
    def test_input_validation(self):
        """Test input validation"""
        # Test empty inputs
        history = llm_bot.get_chat_history("", limit=1)
        self.assertEqual(len(history), 0)
        
        # Test None inputs
        history = llm_bot.get_chat_history(None, limit=1)
        self.assertEqual(len(history), 0)
    
    def test_sync_chat_history(self):
        """Test sync_chat_history function"""
        test_phone = "1234567890"
        test_messages = [
            {"content": "Hello", "timestamp": "2023-01-01T12:00:00"},
            {"content": "How are you?", "timestamp": "2023-01-01T12:01:00"}
        ]
        
        # Sync messages
        llm_bot.sync_chat_history(test_phone, test_messages)
        
        # Verify messages were saved
        history = llm_bot.get_chat_history(test_phone, limit=5)
        self.assertGreater(len(history), 0)

class TestModelAvailability(unittest.TestCase):
    """Test model availability checking"""
    
    @patch('requests.get')
    def test_get_available_model_success(self, mock_get):
        """Test successful model availability check"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "mistral:latest"},
                {"name": "neural-chat:latest"}
            ]
        }
        mock_get.return_value = mock_response
        
        model = llm_bot.get_available_model()
        self.assertIn(model, llm_bot.PREFERRED_MODELS)
    
    @patch('requests.get')
    def test_get_available_model_failure(self, mock_get):
        """Test model availability check failure"""
        # Mock failed response
        mock_get.side_effect = Exception("Connection error")
        
        model = llm_bot.get_available_model()
        self.assertEqual(model, "mistral")  # Should return default

class TestConfigValidation(unittest.TestCase):
    """Test configuration file validation"""
    
    def test_valid_config_structure(self):
        """Test that config file has valid structure"""
        try:
            with open('user_config.json', 'r') as f:
                config = json.load(f)
            
            # Check required structure
            self.assertIn('users', config)
            self.assertIsInstance(config['users'], list)
            
            # Check user structure if users exist
            if config['users']:
                user = config['users'][0]
                required_fields = ['phone', 'tone', 'persona']
                for field in required_fields:
                    self.assertIn(field, user)
                    
        except FileNotFoundError:
            self.skipTest("user_config.json not found")
        except json.JSONDecodeError:
            self.fail("user_config.json is not valid JSON")

def run_basic_validation():
    """Run basic validation checks"""
    print("🔍 Running WhatsApp Bot Code Validation...")
    print("=" * 50)
    
    # Check Python imports
    try:
        import requests
        import sqlite3
        import json
        import datetime
        print("✅ Python dependencies: OK")
    except ImportError as e:
        print(f"❌ Python dependencies: FAILED - {e}")
        return False
    
    # Check if main files exist
    required_files = ['index.js', 'llm_bot.py', 'api_server.py', 'package.json']
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}: EXISTS")
        else:
            print(f"❌ {file}: MISSING")
            return False
    
    # Check package.json structure
    try:
        with open('package.json', 'r') as f:
            package_data = json.load(f)
        
        if 'dependencies' in package_data:
            print("✅ package.json structure: OK")
        else:
            print("❌ package.json structure: INVALID")
            
    except Exception as e:
        print(f"❌ package.json validation: FAILED - {e}")
    
    return True

if __name__ == "__main__":
    # Run basic validation first
    if not run_basic_validation():
        print("\n❌ Basic validation failed!")
        sys.exit(1)
    
    print("\n🧪 Running Unit Tests...")
    print("=" * 50)
    
    # Run unit tests
    unittest.main(verbosity=2, exit=False)
    
    print("\n✅ Code validation completed!")
    print("\nℹ️  Note: To fully test the WhatsApp bot:")
    print("   1. Ensure Ollama is running with a supported model")
    print("   2. Configure user_config.json with actual phone numbers")
    print("   3. Run 'npm start' to start the WhatsApp bot")
    print("   4. Scan QR code with WhatsApp to authenticate")