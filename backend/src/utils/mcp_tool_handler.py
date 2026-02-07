from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseMCPTool(ABC):
    """
    Abstract base class for MCP tools
    """
    
    @abstractmethod
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the tool with the given parameters
        """
        pass


class MCPTodoTool(BaseMCPTool):
    """
    MCP Tool for todo operations
    """
    
    def __init__(self, todo_service):
        self.todo_service = todo_service
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute todo-related operations
        """
        operation = params.get("operation")
        user_id = params.get("user_id")
        
        if not operation or not user_id:
            return {"success": False, "error": "Missing required parameters: operation and user_id"}
        
        try:
            if operation == "create":
                return await self._create_todo(params)
            elif operation == "get":
                return await self._get_todos(params)
            elif operation == "update":
                return await self._update_todo(params)
            elif operation == "delete":
                return await self._delete_todo(params)
            elif operation == "mark_complete":
                return await self._mark_todo_complete(params)
            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}
        except Exception as e:
            logger.error(f"Error executing todo operation {operation}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _create_todo(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new todo
        """
        user_id = params.get("user_id")
        title = params.get("title")
        
        if not title:
            return {"success": False, "error": "Title is required for creating a todo"}
        
        # Prepare todo data
        todo_data = {
            "title": title,
            "description": params.get("description"),
            "priority": params.get("priority", "medium")
        }
        
        # Handle due date if provided
        due_date_str = params.get("due_date")
        if due_date_str:
            from datetime import datetime
            try:
                due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
                todo_data["due_date"] = due_date
            except ValueError:
                return {"success": False, "error": "Invalid date format. Use ISO format."}
        
        # Create the todo using the service
        from ..services.todo_service import TodoService
        todo_service = TodoService()
        db = params.get("db")  # Assuming db session is passed in params
        
        if not db:
            return {"success": False, "error": "Database session not provided"}
        
        todo = todo_service.create_todo(db, todo_data, user_id)
        
        return {
            "success": True,
            "todo_id": str(todo.id),
            "message": f"Created todo: {todo.title}"
        }
    
    async def _get_todos(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get todos for a user
        """
        user_id = params.get("user_id")
        
        # Get todos using the service
        from ..services.todo_service import TodoService
        todo_service = TodoService()
        db = params.get("db")  # Assuming db session is passed in params
        
        if not db:
            return {"success": False, "error": "Database session not provided"}
        
        todos = todo_service.get_todos(db, user_id)
        
        return {
            "success": True,
            "count": len(todos),
            "todos": [
                {
                    "id": str(todo.id),
                    "title": todo.title,
                    "status": todo.status.value,
                    "priority": todo.priority.value,
                    "due_date": todo.due_date.isoformat() if todo.due_date else None,
                    "completed_at": todo.completed_at.isoformat() if todo.completed_at else None
                } for todo in todos
            ]
        }
    
    async def _update_todo(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a todo
        """
        user_id = params.get("user_id")
        todo_id = params.get("todo_id")
        
        if not todo_id:
            return {"success": False, "error": "Todo ID is required for updating"}
        
        # Prepare update data (excluding user_id and todo_id)
        update_data = {k: v for k, v in params.items() 
                      if k not in ["user_id", "todo_id", "operation", "db"]}
        
        # Update the todo using the service
        from ..services.todo_service import TodoService
        todo_service = TodoService()
        db = params.get("db")  # Assuming db session is passed in params
        
        if not db:
            return {"success": False, "error": "Database session not provided"}
        
        from uuid import UUID
        try:
            todo_uuid = UUID(todo_id)
        except ValueError:
            return {"success": False, "error": "Invalid todo ID format"}
        
        updated_todo = todo_service.update_todo(db, todo_uuid, update_data, user_id)
        
        if updated_todo:
            return {
                "success": True,
                "message": f"Updated todo: {updated_todo.title}"
            }
        else:
            return {
                "success": False,
                "error": "Todo not found or unauthorized"
            }
    
    async def _delete_todo(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delete a todo
        """
        user_id = params.get("user_id")
        todo_id = params.get("todo_id")
        
        if not todo_id:
            return {"success": False, "error": "Todo ID is required for deletion"}
        
        # Delete the todo using the service
        from ..services.todo_service import TodoService
        todo_service = TodoService()
        db = params.get("db")  # Assuming db session is passed in params
        
        if not db:
            return {"success": False, "error": "Database session not provided"}
        
        from uuid import UUID
        try:
            todo_uuid = UUID(todo_id)
        except ValueError:
            return {"success": False, "error": "Invalid todo ID format"}
        
        deleted_todo = todo_service.delete_todo(db, todo_uuid, user_id)
        
        if deleted_todo:
            return {
                "success": True,
                "message": f"Deleted todo: {deleted_todo.title}"
            }
        else:
            return {
                "success": False,
                "error": "Todo not found or unauthorized"
            }
    
    async def _mark_todo_complete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mark a todo as complete
        """
        user_id = params.get("user_id")
        todo_id = params.get("todo_id")
        
        if not todo_id:
            return {"success": False, "error": "Todo ID is required to mark complete"}
        
        # Mark the todo as complete using the service
        from ..services.todo_service import TodoService
        todo_service = TodoService()
        db = params.get("db")  # Assuming db session is passed in params
        
        if not db:
            return {"success": False, "error": "Database session not provided"}
        
        from uuid import UUID
        try:
            todo_uuid = UUID(todo_id)
        except ValueError:
            return {"success": False, "error": "Invalid todo ID format"}
        
        completed_todo = todo_service.mark_complete(db, todo_uuid, user_id)
        
        if completed_todo:
            return {
                "success": True,
                "message": f"Marked todo as complete: {completed_todo.title}"
            }
        else:
            return {
                "success": False,
                "error": "Todo not found or unauthorized"
            }


class MCPToolHandler:
    """
    Handler for managing MCP tools
    """
    
    def __init__(self):
        self.tools = {
            "todo": MCPTodoTool(None)  # Todo service will be injected when needed
        }
    
    async def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an MCP tool with the given parameters
        """
        if tool_name not in self.tools:
            return {"success": False, "error": f"Tool '{tool_name}' not found"}
        
        tool = self.tools[tool_name]
        logger.info(f"Executing tool '{tool_name}' with params: {params}")
        
        result = await tool.execute(params)
        
        logger.info(f"Tool '{tool_name}' execution result: {result}")
        return result