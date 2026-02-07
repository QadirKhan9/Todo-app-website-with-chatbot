from fastapi import APIRouter, Depends, HTTPException, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlmodel import Session
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
from ...models.conversation import Conversation
from ...models.message import Message
from ...services.conversation_service import ConversationService
from ...services.message_service import MessageService
from ...dependencies.auth import get_current_user
from ...database import get_db
from ...utils.responses import create_success_response
from ...utils.errors import ValidationError, NotFoundError


limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/conversations", tags=["conversations"])


class CreateConversationRequest(BaseModel):
    title: Optional[str] = None


class UpdateConversationRequest(BaseModel):
    title: Optional[str] = None
    is_active: Optional[bool] = None


@router.post("/", response_model=Conversation)
@limiter.limit("5/minute")
async def create_conversation(
    request: CreateConversationRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new conversation
    """
    try:
        conversation_service = ConversationService()
        
        # Create conversation with provided title or default title
        title = request.title or f"New Conversation {str(current_user.id)[:8]}"
        
        conversation = conversation_service.create_conversation(
            db,
            user_id=current_user.id,
            title=title
        )
        
        return conversation
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating conversation: {str(e)}"
        )


@router.get("/", response_model=List[Conversation])
@limiter.limit("20/minute")
async def get_conversations(
    skip: int = 0,
    limit: int = 20,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all conversations for the current user
    """
    try:
        conversation_service = ConversationService()
        
        conversations = conversation_service.get_conversations(
            db,
            user_id=current_user.id,
            skip=skip,
            limit=limit
        )
        
        return conversations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving conversations: {str(e)}"
        )


@router.get("/{conversation_id}", response_model=Conversation)
@limiter.limit("20/minute")
async def get_conversation(
    conversation_id: UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific conversation by ID
    """
    try:
        conversation_service = ConversationService()
        
        conversation = conversation_service.get_conversation(
            db,
            conversation_id=conversation_id,
            user_id=current_user.id
        )
        
        if not conversation:
            raise NotFoundError(f"Conversation with ID {conversation_id} not found")
        
        return conversation
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID {conversation_id} not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving conversation: {str(e)}"
        )


@router.put("/{conversation_id}", response_model=Conversation)
@limiter.limit("10/minute")
async def update_conversation(
    conversation_id: UUID,
    request: UpdateConversationRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a specific conversation
    """
    try:
        conversation_service = ConversationService()
        
        # Get the conversation to ensure it exists and belongs to the user
        conversation = conversation_service.get_conversation(
            db,
            conversation_id=conversation_id,
            user_id=current_user.id
        )
        
        if not conversation:
            raise NotFoundError(f"Conversation with ID {conversation_id} not found")
        
        # Prepare update data
        update_data = {}
        if request.title is not None:
            update_data["title"] = request.title
        if request.is_active is not None:
            update_data["is_active"] = request.is_active
        
        # Update the conversation
        updated_conversation = conversation_service.update_conversation(
            db,
            conversation_id=conversation_id,
            update_data=update_data
        )
        
        return updated_conversation
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID {conversation_id} not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating conversation: {str(e)}"
        )


@router.delete("/{conversation_id}")
@limiter.limit("5/minute")
async def delete_conversation(
    conversation_id: UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a specific conversation
    """
    try:
        conversation_service = ConversationService()
        
        # Get the conversation to ensure it exists and belongs to the user
        conversation = conversation_service.get_conversation(
            db,
            conversation_id=conversation_id,
            user_id=current_user.id
        )
        
        if not conversation:
            raise NotFoundError(f"Conversation with ID {conversation_id} not found")
        
        # Delete the conversation
        success = conversation_service.delete_conversation(
            db,
            conversation_id=conversation_id
        )
        
        if success:
            return {"message": f"Conversation {conversation_id} deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete conversation"
            )
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID {conversation_id} not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting conversation: {str(e)}"
        )


@router.get("/{conversation_id}/messages")
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