#!/usr/bin/env python3
"""
Test script to verify Google Gemini API integration
"""
import asyncio
import os
import sys
from pathlib import Path

# Add the project root and backend to the Python path
project_root = Path(__file__).parent
backend_dir = project_root / "backend"
backend_src = backend_dir / "src"

sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(backend_src))

os.chdir(backend_dir)  # Change working directory to backend

from src.config.settings import get_settings
from src.services.ai_agent_service import AIAgentService

async def test_gemini_connection():
    print("Testing Google Gemini API connection...")
    
    # Get settings
    settings = get_settings()
    print(f"Google API Key loaded: {'Yes' if settings.GOOGLE_API_KEY else 'No'}")
    print(f"Gemini Model: {settings.GEMINI_MODEL}")
    
    # Initialize AI agent service
    ai_service = AIAgentService()
    
    try:
        # Test a simple message
        print("\nTesting a simple message...")
        response = await ai_service.model.generate_content_async("Hello, how are you?")
        print(f"Response: {response.text}")
        print("✓ Gemini API connection is working!")
    except Exception as e:
        print(f"✗ Error connecting to Gemini API: {e}")
        
        # Try to test with the full chat interface
        try:
            print("\nTesting with chat interface...")
            chat = ai_service.model.start_chat()
            response = await chat.send_message_async("Hello, how are you?")
            print(f"Chat response: {response.text}")
            print("✓ Gemini chat interface is working!")
        except Exception as e2:
            print(f"✗ Error with chat interface: {e2}")
    
    # Test the AI agent's process_message method
    try:
        print("\nTesting AI agent process_message method...")
        result = await ai_service.process_message(
            conversation_id="test_conv",
            user_message="Hello, how are you?",
            user_id="test_user"
        )
        print(f"Process message result: {result}")
        print("✓ AI agent process_message is working!")
    except Exception as e3:
        print(f"✗ Error in process_message: {e3}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_gemini_connection())