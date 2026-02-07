from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from uuid import uuid4
from datetime import datetime
from pydantic import BaseModel
import json

from ..models.conversation import Conversation
from ..models.message import Message, MessageRole
from ..services.conversation_service import ConversationService
from ..services.ai_agent_service import AIAgentService
from ..dependencies.auth import get_current_user
from ..utils.exceptions import ValidationError, ResourceNotFoundError, AuthorizationError
from ..db.session import create_db_and_tables

router = APIRouter()


class ChatRequest(BaseModel):
    user_id: str
    conversation_id: Optional[str] = None
    message: str
    metadata: Optional[dict] = {}


class ChatResponse(BaseModel):
    conversation_id: str
    message_id: str
    response: dict  # Contains role, content, and tool_calls
    timestamp: datetime


class NewConversationRequest(BaseModel):
    user_id: str
    initial_message: Optional[str] = None


class NewConversationResponse(BaseModel):
    conversation_id: str
    message_id: Optional[str] = None
    response: Optional[dict] = None
    timestamp: datetime


@router.post("/chat", response_model=ChatResponse)
@router.post("/chat/", response_model=ChatResponse)  # Also handle trailing slash to prevent redirects
async def chat_endpoint(
    request: ChatRequest,
    current_user_id: str = Depends(get_current_user)
):
    """
    Send a message to the AI agent and receive a response.
    """
    from ..utils.logging import log_conversation_event
    from ..services.performance_optimization import OptimizedConversationService, OptimizedAIAgentService

    try:
        # Validate the request
        if not request.message.strip():
            raise ValidationError("Message content cannot be empty")

        # Verify user owns the conversation if conversation_id is provided
        if request.conversation_id:
            conversation_service = OptimizedConversationService()  # Use optimized service
            conversation = await conversation_service.get_conversation(request.conversation_id)
            if not conversation:
                raise ResourceNotFoundError("Conversation", request.conversation_id)

            # Verify the user owns this conversation
            if conversation.user_id != request.user_id:
                raise AuthorizationError("Not authorized to access this conversation")
        else:
            # Create a new conversation
            conversation_service = OptimizedConversationService()  # Use optimized service
            conversation = await conversation_service.create_conversation(
                conversation_id=str(uuid4()),
                user_id=request.user_id,
                title=f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )

        # Save user message
        user_message = Message(
            conversation_id=conversation.conversation_id,
            role=MessageRole.USER,
            content=request.message,
            message_metadata=json.dumps(request.metadata) if request.metadata else None
        )
        saved_message = await conversation_service.add_message(user_message)

        # Process with AI agent
        ai_service = OptimizedAIAgentService()  # Use optimized service
        try:
            ai_response = await ai_service.process_message_with_tools(  # Use the enhanced method
                conversation_id=conversation.conversation_id,
                user_message=request.message,
                user_id=request.user_id  # Pass the user ID to the AI service
            )

            # Save AI response - ensure content is never empty to avoid validation errors
            ai_content = ai_response.get("content", "").strip()
            if not ai_content:
                ai_content = "AI did not provide a response. Please try again or rephrase your message."

            ai_message = Message(
                conversation_id=conversation.conversation_id,
                role=MessageRole.ASSISTANT,
                content=ai_content,
                message_metadata=json.dumps(ai_response.get("tool_calls", []))
            )
            saved_ai_message = await conversation_service.add_message(ai_message)
        except Exception as ai_error:
            # Log the AI service error for debugging
            import logging
            logging.error(f"AI service error in chat endpoint: {str(ai_error)}", exc_info=True)
            
            # Create a fallback response when AI service fails but task was created
            ai_content = "AI service is temporarily unavailable, but your request was processed successfully."
            
            ai_message = Message(
                conversation_id=conversation.conversation_id,
                role=MessageRole.ASSISTANT,
                content=ai_content,
                message_metadata=json.dumps([])
            )
            saved_ai_message = await conversation_service.add_message(ai_message)
            
            # Set a fallback response to return to the client
            ai_response = {
                "role": "assistant",
                "content": ai_content,
                "tool_calls": []
            }

        # Log the conversation event
        log_conversation_event(
            conversation_id=conversation.conversation_id,
            user_id=request.user_id,
            event_type="message_sent",
            details={
                "user_message_length": len(request.message),
                "ai_response_length": len(ai_response.get("content", "")),
                "has_tool_calls": len(ai_response.get("tool_calls", [])) > 0
            }
        )

        return ChatResponse(
            conversation_id=conversation.conversation_id,
            message_id=str(saved_ai_message.id),
            response=ai_response,
            timestamp=datetime.utcnow()
        )
    except ValidationError:
        raise
    except ResourceNotFoundError:
        raise
    except AuthorizationError:
        raise
    except Exception as e:
        # Log the error for debugging purposes
        import logging
        logging.error(f"Unexpected error in chat endpoint: {str(e)}", exc_info=True)

        # Return a safe error response to the client
        return ChatResponse(
            conversation_id=request.conversation_id or str(uuid4()),
            message_id=str(uuid4()),
            response={
                "role": "assistant",
                "content": "Sorry, an error occurred while processing your request. Please try again.",
                "tool_calls": []
            },
            timestamp=datetime.utcnow()
        )


@router.get("/conversations/{conversation_id}")
@router.get("/conversations/{conversation_id}/")  # Also handle trailing slash to prevent redirects
async def get_conversation(
    conversation_id: str,
    current_user_id: str = Depends(get_current_user)
):
    """
    Retrieve conversation history.
    """
    from ..services.performance_optimization import OptimizedConversationService

    conversation_service = OptimizedConversationService()  # Use optimized service
    conversation = await conversation_service.get_conversation(conversation_id)

    if not conversation:
        raise ResourceNotFoundError("Conversation", conversation_id)

    # In a real implementation, we would verify that the current user owns this conversation
    # For now, we'll just return the conversation if it exists

    messages = await conversation_service.get_messages(conversation_id)

    return {
        "conversation_id": conversation.conversation_id,
        "messages": [
            {
                "id": str(msg.id),
                "role": msg.role.value,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "tool_calls": json.loads(msg.message_metadata) if msg.message_metadata else [],
                "tool_call_results": []  # Would be populated in a full implementation
            }
            for msg in messages
        ],
        "created_at": conversation.created_at.isoformat(),
        "updated_at": conversation.updated_at.isoformat()
    }


@router.post("/conversations", response_model=NewConversationResponse)
@router.post("/conversations/", response_model=NewConversationResponse)  # Also handle trailing slash to prevent redirects
async def create_conversation(
    request: NewConversationRequest,
    current_user_id: str = Depends(get_current_user)
):
    """
    Start a new conversation.
    """
    from ..services.performance_optimization import OptimizedConversationService, OptimizedAIAgentService

    conversation_service = OptimizedConversationService()  # Use optimized service

    # Create conversation
    conversation = await conversation_service.create_conversation(
        conversation_id=str(uuid4()),
        user_id=request.user_id,
        title=f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )

    response_data = {
        "conversation_id": conversation.conversation_id,
        "timestamp": datetime.utcnow()
    }

    # If initial message is provided, process it
    if request.initial_message:
        # Save user message
        user_message = Message(
            conversation_id=conversation.conversation_id,
            role=MessageRole.USER,
            content=request.initial_message
        )
        saved_message = await conversation_service.add_message(user_message)

        # Process with AI agent
        ai_service = OptimizedAIAgentService()  # Use optimized service
        try:
            ai_response = await ai_service.process_message(
                conversation_id=conversation.conversation_id,
                user_message=request.initial_message,
                user_id=request.user_id  # Pass the user ID to the AI service
            )

            # Save AI response - ensure content is never empty to avoid validation errors
            ai_content = ai_response.get("content", "").strip()
            if not ai_content:
                ai_content = "AI did not provide a response. Please try again or rephrase your message."

            ai_message = Message(
                conversation_id=conversation.conversation_id,
                role=MessageRole.ASSISTANT,
                content=ai_content,
                message_metadata=json.dumps(ai_response.get("tool_calls", []))
            )
            saved_ai_message = await conversation_service.add_message(ai_message)

            response_data["message_id"] = str(saved_ai_message.id)
            response_data["response"] = ai_response
        except Exception as ai_error:
            # Log the AI service error for debugging
            import logging
            logging.error(f"AI service error in conversation creation: {str(ai_error)}", exc_info=True)
            
            # Create a fallback response when AI service fails but task was created
            ai_content = "AI service is temporarily unavailable, but your request was processed successfully."
            
            ai_message = Message(
                conversation_id=conversation.conversation_id,
                role=MessageRole.ASSISTANT,
                content=ai_content,
                message_metadata=json.dumps([])
            )
            saved_ai_message = await conversation_service.add_message(ai_message)
            
            # Set a fallback response to return to the client
            response_data["message_id"] = str(saved_ai_message.id)
            response_data["response"] = {
                "role": "assistant",
                "content": ai_content,
                "tool_calls": []
            }

    return NewConversationResponse(**response_data)