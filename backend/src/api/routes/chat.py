from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from sqlmodel import Session
from typing import Dict, Any
from uuid import UUID
import uuid
from pydantic import BaseModel
from ...models.message import Message, MessageBase
from ...services.ai_agent_service import AIAgentService
from ...services.message_service import MessageService
from ...services.conversation_service import ConversationService
from ...dependencies.auth import get_current_user
from ...database import get_db
from ...utils.responses import create_success_response
from ...utils.errors import ValidationError, NotFoundError


limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    conversation_id: str
    message_id: str
    response: str
    action_taken: Dict[str, Any]
    timestamp: str


@router.post("/", response_model=ChatResponse)
@limiter.limit("10/minute")
async def chat_with_ai(
    request: ChatRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Process a user's message and return the AI response
    """
    try:
        # Create an instance of the AI agent service
        ai_agent_service = AIAgentService()
        
        # Generate a new conversation ID if not provided
        # For simplicity, we'll create a new conversation for each request
        # In a real implementation, you'd likely pass the conversation ID
        conversation_service = ConversationService()
        conversation = conversation_service.create_conversation(
            db, 
            user_id=current_user.id, 
            title=f"Chat on {str(uuid.uuid4())[:8]}"
        )
        
        # Create a message for the user's input
        message_service = MessageService()
        user_message = message_service.create_message(
            db,
            conversation_id=conversation.id,
            role="user",
            content=request.message
        )
        
        # Process the message with the AI agent
        result = await ai_agent_service.process_user_message(
            db,
            str(current_user.id),
            str(conversation.id),
            request.message
        )
        
        # Create a message for the AI's response
        ai_message = message_service.create_message(
            db,
            conversation_id=conversation.id,
            role="assistant",
            content=result["response"],
            message_type="standard"
        )
        
        from datetime import datetime
        return ChatResponse(
            conversation_id=str(conversation.id),
            message_id=str(ai_message.id),
            response=result["response"],
            action_taken=result["action_taken"],
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat request: {str(e)}"
        )


@router.post("/conversations/{conversation_id}", response_model=ChatResponse)
@limiter.limit("10/minute")
async def chat_with_ai_in_conversation(
    conversation_id: UUID,
    request: ChatRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Process a user's message in an existing conversation and return the AI response
    """
    try:
        # Verify that the conversation belongs to the user
        conversation_service = ConversationService()
        conversation = conversation_service.get_conversation(db, conversation_id, current_user.id)
        
        if not conversation:
            raise NotFoundError(f"Conversation with ID {conversation_id} not found")
        
        # Create an instance of the AI agent service
        ai_agent_service = AIAgentService()
        
        # Create a message for the user's input
        message_service = MessageService()
        user_message = message_service.create_message(
            db,
            conversation_id=conversation.id,
            role="user",
            content=request.message
        )
        
        # Process the message with the AI agent
        result = await ai_agent_service.process_user_message(
            db,
            str(current_user.id),
            str(conversation.id),
            request.message
        )
        
        # Create a message for the AI's response
        ai_message = message_service.create_message(
            db,
            conversation_id=conversation.id,
            role="assistant",
            content=result["response"],
            message_type="standard"
        )
        
        from datetime import datetime
        return ChatResponse(
            conversation_id=str(conversation.id),
            message_id=str(ai_message.id),
            response=result["response"],
            action_taken=result["action_taken"],
            timestamp=datetime.utcnow().isoformat()
        )
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID {conversation_id} not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat request: {str(e)}"
        )


@router.get("/conversations/{conversation_id}/messages")
@limiter.limit("20/minute")
async def get_conversation_messages(
    conversation_id: UUID,
    skip: int = 0,
    limit: int = 100,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get messages for a specific conversation
    """
    try:
        # Verify that the conversation belongs to the user
        conversation_service = ConversationService()
        conversation = conversation_service.get_conversation(db, conversation_id, current_user.id)
        
        if not conversation:
            raise NotFoundError(f"Conversation with ID {conversation_id} not found")
        
        # Get messages for the conversation
        message_service = MessageService()
        messages = message_service.get_messages_for_conversation(
            db, 
            conversation_id, 
            skip=skip, 
            limit=limit
        )
        
        return {
            "conversation_id": str(conversation.id),
            "messages": [
                {
                    "id": str(msg.id),
                    "role": msg.role.value,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "type": msg.message_type.value
                } for msg in messages
            ]
        }
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID {conversation_id} not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving messages: {str(e)}"
        )