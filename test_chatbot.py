#!/usr/bin/env python3
"""
Test script to verify chatbot functionality
"""
import asyncio
import aiohttp
import json
from uuid import uuid4

async def test_chatbot():
    base_url = "http://127.0.0.1:8000"
    
    print("Testing chatbot functionality...")
    
    # Test 1: Create a new conversation
    print("\n1. Creating a new conversation...")
    try:
        async with aiohttp.ClientSession() as session:
            # Create a new conversation
            new_conv_data = {
                "user_id": str(uuid4()),  # Using a random UUID for testing
                "initial_message": "Hello, how are you?"
            }
            
            async with session.post(f"{base_url}/v1/conversations", json=new_conv_data) as response:
                conv_response = await response.json()
                print(f"Conversation response: {json.dumps(conv_response, indent=2)}")
                
                if response.status != 200:
                    print(f"Error creating conversation: {response.status}")
                    return
                
                conversation_id = conv_response.get("conversation_id")
                print(f"Created conversation with ID: {conversation_id}")
                
                # Test 2: Send a follow-up message to the conversation
                print("\n2. Sending a follow-up message...")
                chat_data = {
                    "user_id": new_conv_data["user_id"],
                    "conversation_id": conversation_id,
                    "message": "What can you help me with?"
                }
                
                async with session.post(f"{base_url}/v1/chat", json=chat_data) as chat_response:
                    chat_resp = await chat_response.json()
                    print(f"Chat response: {json.dumps(chat_resp, indent=2)}")
                    
                    if chat_response.status != 200:
                        print(f"Error sending chat message: {chat_response.status}")
                        return
                    
                    print("✓ Chatbot functionality test completed successfully!")
                    
    except Exception as e:
        print(f"Error during chatbot test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_chatbot())