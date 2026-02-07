from typing import Dict, Any, Optional
import asyncio
import aiohttp
import uuid
from sqlmodel import Session, select, func
from ..config.settings import get_settings
from ..models.task import TaskCreate
from ..models.user_model import User
from ..db.session import sync_engine
from . import task_service


class ToolExecutionService:
    """
    Service class to handle execution of tools requested by the AI agent.
    This service manages communication with the MCP server and other external tools.
    """

    def __init__(self):
        self.settings = get_settings()

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool with the given name and arguments.
        """
        # Handle task-related tools
        if tool_name == "create_task":
            return await self._execute_create_task(arguments)
        elif tool_name == "delete_task":
            return await self._execute_delete_task(arguments)
        elif tool_name == "update_task":
            return await self._execute_update_task(arguments)
        elif tool_name == "list_tasks":
            return await self._execute_list_tasks(arguments)
        elif tool_name == "edit_task_title":
            return await self._execute_edit_task_title(arguments)
        elif tool_name == "get_current_time":
            return {
                "current_time": asyncio.get_event_loop().time(),
                "timezone": "UTC"
            }
        elif tool_name == "search_web":
            # Simulate a web search
            query = arguments.get("query", "")
            return {
                "results": [f"Simulated search results for: {query}"],
                "query": query
            }
        elif tool_name == "calculate":
            # Simulate a calculation
            expression = arguments.get("expression", "")
            try:
                # Note: In a real implementation, you'd want to use a safer evaluation method
                result = eval(expression)  # NOQA
                return {
                    "result": result,
                    "expression": expression
                }
            except Exception:
                return {
                    "error": "Invalid expression",
                    "expression": expression
                }
        else:
            # For other tools, make a call to the MCP server
            return await self.execute_mcp_tool(tool_name, arguments)

    async def _execute_create_task(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the create_task tool to create a new task in the database.
        """
        try:
            # Extract task properties from arguments
            title = arguments.get("title", "")
            description = arguments.get("description", "")
            user_id = arguments.get("user_id", "")  # User ID should be passed from the conversation context

            if not title:
                return {
                    "error": "Title is required to create a task"
                }

            if not user_id:
                return {
                    "error": "User ID is required to create a task"
                }

            # Create a todo using the todo service (which we know works)
            with Session(sync_engine) as db_session:
                # Verify the user exists - convert string to UUID
                user_uuid = uuid.UUID(user_id)
                user = db_session.get(User, user_uuid)
                if not user:
                    return {
                        "error": f"User with ID {user_id} not found"
                    }

                # Create the todo using the todo service function
                from ..models.todo import TodoBase, TodoStatus, TodoPriority
                from .todo_service import TodoService

                # Prepare todo data
                todo_data = {
                    "title": title,
                    "description": description or "",
                    "status": TodoStatus.PENDING,
                    "priority": TodoPriority.MEDIUM
                }

                # Use the todo service to create the todo
                todo_service = TodoService()
                created_todo = todo_service.create_todo(db_session, todo_data, user_id)

                return {
                    "success": True,
                    "task_id": str(created_todo.id),  # Using task_id for consistency
                    "title": created_todo.title,
                    "description": created_todo.description,
                    "status": created_todo.status,
                    "message": f"Task '{created_todo.title}' created successfully"
                }

        except Exception as e:
            return {
                "error": f"Failed to create task: {str(e)}"
            }

    async def _execute_delete_task(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the delete_task tool to delete a task from the database.
        """
        try:
            # Extract task properties from arguments
            title = arguments.get("title", "")
            user_id = arguments.get("user_id", "")  # User ID should be passed from the conversation context

            if not title:
                return {
                    "error": "Title is required to delete a task"
                }

            if not user_id:
                return {
                    "error": "User ID is required to delete a task"
                }

            # Delete a todo using the todo service
            with Session(sync_engine) as db_session:
                # Verify the user exists - convert string to UUID
                user_uuid = uuid.UUID(user_id)
                user = db_session.get(User, user_uuid)
                if not user:
                    return {
                        "error": f"User with ID {user_id} not found"
                    }

                # Find the todo by title and user_id
                from sqlmodel import select, func
                from ..models.todo import Todo, TodoStatus
                from .todo_service import TodoService

                # Find the todo by title and user_id
                # Convert the user_id string to UUID object
                user_uuid = uuid.UUID(user_id)
                
                # First, try exact match
                statement = select(Todo).where(
                    Todo.title == title,  # Exact match first
                    Todo.user_id == user_uuid
                )
                result = db_session.exec(statement)
                todo = result.first()
                
                # If no exact match found, try case-insensitive exact match
                if not todo:
                    statement = select(Todo).where(
                        func.lower(Todo.title) == func.lower(title),  # Case-insensitive exact match
                        Todo.user_id == user_uuid
                    )
                    result = db_session.exec(statement)
                    todo = result.first()
                
                if not todo:
                    return {
                        "error": f"No task found with title '{title}'"
                    }

                # Use the todo service to delete the todo
                todo_service = TodoService()
                success = todo_service.delete_todo(db_session, str(todo.id), user_id)

                if success:
                    return {
                        "success": True,
                        "task_id": str(todo.id),
                        "title": todo.title,
                        "message": f"Task '{todo.title}' deleted successfully"
                    }
                else:
                    return {
                        "error": f"Failed to delete task '{title}'"
                    }

        except Exception as e:
            return {
                "error": f"Failed to delete task: {str(e)}"
            }

    async def _execute_update_task(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the update_task tool to update a task in the database.
        """
        try:
            # Extract task properties from arguments
            title = arguments.get("title", "")
            new_status = arguments.get("status", "")
            user_id = arguments.get("user_id", "")  # User ID should be passed from the conversation context

            if not title:
                return {
                    "error": "Title is required to update a task"
                }

            if not user_id:
                return {
                    "error": "User ID is required to update a task"
                }

            # Update a todo using the todo service
            with Session(sync_engine) as db_session:
                # Verify the user exists - convert string to UUID
                user_uuid = uuid.UUID(user_id)
                user = db_session.get(User, user_uuid)
                if not user:
                    return {
                        "error": f"User with ID {user_id} not found"
                    }

                # Find the todo by title and user_id
                from sqlmodel import select, func
                from ..models.todo import Todo, TodoStatus
                from .todo_service import TodoService

                # Find the todo by title and user_id
                # Convert the user_id string to UUID object
                user_uuid = uuid.UUID(user_id)
                
                # First, try exact match
                statement = select(Todo).where(
                    Todo.title == title,  # Exact match first
                    Todo.user_id == user_uuid
                )
                result = db_session.exec(statement)
                todo = result.first()
                
                # If no exact match found, try case-insensitive exact match
                if not todo:
                    statement = select(Todo).where(
                        func.lower(Todo.title) == func.lower(title),  # Case-insensitive exact match
                        Todo.user_id == user_uuid
                    )
                    result = db_session.exec(statement)
                    todo = result.first()
                
                if not todo:
                    return {
                        "error": f"No task found with title '{title}'"
                    }

                # Prepare update data
                from ..models.todo import TodoStatus
                status_map = {
                    "completed": TodoStatus.COMPLETED,
                    "done": TodoStatus.COMPLETED,
                    "finished": TodoStatus.COMPLETED,
                    "pending": TodoStatus.PENDING,
                    "in_progress": TodoStatus.IN_PROGRESS,
                    "todo": TodoStatus.PENDING
                }

                update_status = status_map.get(new_status.lower(), todo.status)

                update_data = {
                    "status": update_status
                }

                # Use the todo service to update the todo
                todo_service = TodoService()
                updated_todo = todo_service.update_todo(db_session, str(todo.id), update_data, user_id)

                if updated_todo:
                    status_text = "completed" if updated_todo.status == TodoStatus.COMPLETED else "updated"
                    return {
                        "success": True,
                        "task_id": str(updated_todo.id),
                        "title": updated_todo.title,
                        "status": str(updated_todo.status),
                        "message": f"Task '{updated_todo.title}' {status_text} successfully"
                    }
                else:
                    return {
                        "error": f"Failed to update task '{title}'"
                    }

        except Exception as e:
            return {
                "error": f"Failed to update task: {str(e)}"
            }

    async def _execute_list_tasks(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the list_tasks tool to retrieve all tasks for a user.
        """
        try:
            # Extract user_id from arguments
            user_id = arguments.get("user_id", "")

            if not user_id:
                return {
                    "error": "User ID is required to list tasks"
                }

            # List todos using the todo service
            with Session(sync_engine) as db_session:
                # Verify the user exists - convert string to UUID
                user_uuid = uuid.UUID(user_id)
                user = db_session.get(User, user_uuid)
                if not user:
                    return {
                        "error": f"User with ID {user_id} not found"
                    }

                # Find all todos for the user
                from sqlmodel import select
                from ..models.todo import Todo
                from .todo_service import TodoService

                # Find all todos by user_id
                user_uuid = uuid.UUID(user_id)
                statement = select(Todo).where(
                    Todo.user_id == user_uuid
                )
                result = db_session.exec(statement)
                todos = result.all()

                # Convert todos to a list of dictionaries
                tasks = []
                for todo in todos:
                    task_dict = {
                        "id": str(todo.id),
                        "title": todo.title,
                        "description": todo.description or "",
                        "status": str(todo.status),
                        "priority": str(todo.priority) if hasattr(todo, 'priority') else "medium",
                        "created_at": todo.created_at.isoformat() if hasattr(todo, 'created_at') else None,
                        "updated_at": todo.updated_at.isoformat() if hasattr(todo, 'updated_at') else None
                    }
                    tasks.append(task_dict)

                return {
                    "success": True,
                    "tasks": tasks,
                    "count": len(tasks),
                    "message": f"Retrieved {len(tasks)} tasks for the user"
                }

        except Exception as e:
            return {
                "error": f"Failed to list tasks: {str(e)}"
            }

    async def _execute_edit_task_title(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the edit_task_title tool to update a task's title in the database.
        """
        try:
            # Extract task properties from arguments
            old_title = arguments.get("old_title", "")
            new_title = arguments.get("new_title", "")
            user_id = arguments.get("user_id", "")  # User ID should be passed from the conversation context

            if not old_title or not new_title:
                return {
                    "error": "Both old title and new title are required to edit a task"
                }

            if not user_id:
                return {
                    "error": "User ID is required to edit a task"
                }

            # Update a todo using the todo service
            with Session(sync_engine) as db_session:
                # Verify the user exists - convert string to UUID
                user_uuid = uuid.UUID(user_id)
                user = db_session.get(User, user_uuid)
                if not user:
                    return {
                        "error": f"User with ID {user_id} not found"
                    }

                # Find the todo by old title and user_id
                from sqlmodel import select
                from ..models.todo import Todo
                from .todo_service import TodoService

                # Find the todo by exact title match and user_id
                user_uuid = uuid.UUID(user_id)
                
                # First, try exact match
                statement = select(Todo).where(
                    Todo.title == old_title,  # Exact match first
                    Todo.user_id == user_uuid
                )
                result = db_session.exec(statement)
                todo = result.first()
                
                # If no exact match found, try case-insensitive exact match
                if not todo:
                    statement = select(Todo).where(
                        func.lower(Todo.title) == func.lower(old_title),  # Case-insensitive exact match
                        Todo.user_id == user_uuid
                    )
                    result = db_session.exec(statement)
                    todo = result.first()

                if not todo:
                    return {
                        "error": f"No task found with title '{old_title}'"
                    }

                # Prepare update data
                update_data = {
                    "title": new_title
                }

                # Use the todo service to update the todo
                todo_service = TodoService()
                updated_todo = todo_service.update_todo(db_session, str(todo.id), update_data, user_id)

                if updated_todo:
                    return {
                        "success": True,
                        "task_id": str(updated_todo.id),
                        "old_title": old_title,
                        "new_title": updated_todo.title,
                        "message": f"Task title updated from '{old_title}' to '{updated_todo.title}' successfully"
                    }
                else:
                    return {
                        "error": f"Failed to update task title from '{old_title}' to '{new_title}'"
                    }

        except Exception as e:
            return {
                "error": f"Failed to edit task title: {str(e)}"
            }

    async def execute_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool via the MCP server.
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.settings.MCP_SERVER_URL}/tools/{tool_name}"
                payload = {
                    "arguments": arguments
                }

                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result
                    else:
                        error_text = await response.text()
                        return {
                            "error": f"MCP tool execution failed: {error_text}",
                            "status_code": response.status
                        }
        except Exception as e:
            return {
                "error": f"Failed to execute MCP tool: {str(e)}"
            }