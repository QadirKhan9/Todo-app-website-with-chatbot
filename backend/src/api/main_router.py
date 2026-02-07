from fastapi import APIRouter
from .dependencies import get_current_user


# Main API router
api_router = APIRouter()

# Import and include specific routers
from .auth import router as auth_router
from .chat_router import router as chat_router
from .tasks import router as tasks_router
from .todos import router as todos_router

api_router.include_router(auth_router)
api_router.include_router(chat_router, prefix="/v1", tags=["chat"])
api_router.include_router(tasks_router, prefix="/v1", tags=["tasks"])
api_router.include_router(todos_router, tags=["todos"])