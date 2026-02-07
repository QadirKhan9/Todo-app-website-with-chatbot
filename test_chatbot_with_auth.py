#!/usr/bin/env python3
"""
Test script to verify chatbot functionality with proper authentication
"""
import asyncio
import aiohttp
import json
from uuid import uuid4

async def test_chatbot_with_auth():
    base_url = "http://127.0.0.1:8000"
    
    print("Testing chatbot functionality with authentication...")
    
    # First, register a test user
    print("\n1. Registering a test user...")
    try:
        async with aiohttp.ClientSession() as session:
            # Register a new user
            user_data = {
                "email": f"testuser_{uuid4()}@example.com",
                "password": "TestPassword123!",
                "username": f"testuser_{str(uuid4())[:8]}"
            }
            
            async with session.post(f"{base_url}/api/v1/auth/signup", json=user_data) as signup_response:
                signup_result = await signup_response.json()
                print(f"Signup response status: {signup_response.status}")
                
                if signup_response.status != 200:
                    print(f"Signup failed: {signup_result}")
                    return
                
                access_token = signup_result.get("access_token")
                user_id = signup_result.get("user", {}).get("id")
                
                print(f"User registered successfully. User ID: {user_id}")
                
                # Now test the chat functionality with the token
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
                
                # Test 2: Create a new conversation
                print("\n2. Creating a new conversation with authentication...")
                new_conv_data = {
                    "user_id": user_id,
                    "initial_message": "Hello, how are you?"
                }
                
                async with session.post(f"{base_url}/v1/conversations", json=new_conv_data, headers=headers) as conv_response:
                    conv_result = await conv_response.json()
                    print(f"Conversation response status: {conv_response.status}")
                    print(f"Conversation response: {json.dumps(conv_result, indent=2)}")
                    
                    if conv_response.status != 200:
                        print(f"Error creating conversation: {conv_result}")
                        return
                    
                    conversation_id = conv_result.get("conversation_id")
                    print(f"Created conversation with ID: {conversation_id}")
                    
                    # Test 3: Send a follow-up message to the conversation
                    print("\n3. Sending a follow-up message...")
                    chat_data = {
                        "user_id": user_id,
                        "conversation_id": conversation_id,
                        "message": "What can you help me with?"
                    }
                    
                    async with session.post(f"{base_url}/v1/chat", json=chat_data, headers=headers) as chat_response:
                        chat_result = await chat_response.json()
                        print(f"Chat response status: {chat_response.status}")
                        print(f"Chat response: {json.dumps(chat_result, indent=2)}")
                        
                        if chat_response.status != 200:
                            print(f"Error sending chat message: {chat_result}")
                            return
                        
                        print("\n✓ Chatbot functionality test completed successfully!")
                        
    except Exception as e:
        print(f"Error during chatbot test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_chatbot_with_auth())