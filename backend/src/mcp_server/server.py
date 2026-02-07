import asyncio
from typing import Dict, Any, List
from backend.src.mcp_server import Server
from mcp.types import TextContent, Prompt, PromptResult, Tool, ToolCallResult
import json
from backend.src.tools.add_task import add_task_handler
from backend.src.tools.list_tasks import list_tasks_handler
from backend.src.tools.complete_task import complete_task_handler
from backend.src.tools.update_task import update_task_handler
from backend.src.tools.delete_task import delete_task_handler
from backend.src.auth.jwt import get_current_user, verify_token
from backend.src.database.session import get_session
from backend.src.models.responses import (
    AddTaskResponse, ListTasksResponse, TaskOperationResponse, ErrorResponse
)

# Initialize the MCP server
server = Server("todo-ai-chatbot-mcp-server")

@server.list_prompts()
async def list_prompts() -> List[Prompt]:
    """List available prompts."""
    return []

@server.get_prompt()
async def get_prompt(name: str) -> PromptResult:
    """Get a specific prompt."""
    return PromptResult(
        messages=[
            TextContent(
                type="text",
                text=f"Prompt '{name}' not found."
            )
        ]
    )

# Helper function to extract user ID from headers
def extract_user_id_from_headers(headers: Dict[str, str]) -> str:
    """Extract user ID from authorization header."""
    auth_header = headers.get("authorization", "")
    if not auth_header.startswith("Bearer "):
        raise ValueError("Invalid authorization header format")

    token = auth_header[7:]  # Remove "Bearer " prefix
    token_data = verify_token(token)
    if not token_data:
        raise ValueError("Invalid or expired token")

    return token_data.user_id

# Register the add_task tool
@server.call_tool()
async def add_task_tool(context, arguments: Dict[str, Any]) -> ToolCallResult:
    """
    Tool to add a new task for the authenticated user.

    Arguments:
    - title: The title of the task (required)
    - description: The description of the task (optional)
    """
    try:
        # Extract user ID from context (headers)
        user_id = extract_user_id_from_headers(context.headers)

        # Call the actual handler
        result = await add_task_handler(
            title=arguments["title"],
            description=arguments.get("description"),
            user_id=user_id
        )

        return ToolCallResult(
            content=[
                TextContent(
                    type="text",
                    text=json.dumps(result.dict())
                )
            ]
        )
    except Exception as e:
        error_result = ErrorResponse(
            success=False,
            error=str(e),
            error_code="ADD_TASK_ERROR"
        )
        return ToolCallResult(
            content=[
                TextContent(
                    type="text",
                    text=json.dumps(error_result.dict())
                )
            ]
        )

# Register the list_tasks tool
@server.call_tool()
async def list_tasks_tool(context, arguments: Dict[str, Any]) -> ToolCallResult:
    """
    Tool to list tasks for the authenticated user.

    Arguments:
    - status: Filter tasks by status (optional, default: "all")
    """
    try:
        # Extract user ID from context (headers)
        user_id = extract_user_id_from_headers(context.headers)

        # Call the actual handler
        result = await list_tasks_handler(
            user_id=user_id,
            status=arguments.get("status", "all")
        )

        return ToolCallResult(
            content=[
                TextContent(
                    type="text",
                    text=json.dumps(result.dict())
                )
            ]
        )
    except Exception as e:
        error_result = ErrorResponse(
            success=False,
            error=str(e),
            error_code="LIST_TASKS_ERROR"
        )
        return ToolCallResult(
            content=[
                TextContent(
                    type="text",
                    text=json.dumps(error_result.dict())
                )
            ]
        )

# Register the complete_task tool
@server.call_tool()
async def complete_task_tool(context, arguments: Dict[str, Any]) -> ToolCallResult:
    """
    Tool to mark a task as completed for the authenticated user.

    Arguments:
    - task_id: The ID of the task to complete
    """
    try:
        # Extract user ID from context (headers)
        user_id = extract_user_id_from_headers(context.headers)

        # Call the actual handler
        result = await complete_task_handler(
            task_id=arguments["task_id"],
            user_id=user_id
        )

        return ToolCallResult(
            content=[
                TextContent(
                    type="text",
                    text=json.dumps(result.dict())
                )
            ]
        )
    except Exception as e:
        error_result = ErrorResponse(
            success=False,
            error=str(e),
            error_code="COMPLETE_TASK_ERROR"
        )
        return ToolCallResult(
            content=[
                TextContent(
                    type="text",
                    text=json.dumps(error_result.dict())
                )
            ]
        )

# Register the update_task tool
@server.call_tool()
async def update_task_tool(context, arguments: Dict[str, Any]) -> ToolCallResult:
    """
    Tool to update a task for the authenticated user.

    Arguments:
    - task_id: The ID of the task to update
    - title: New title (optional)
    - description: New description (optional)
    - status: New status (optional)
    """
    try:
        # Extract user ID from context (headers)
        user_id = extract_user_id_from_headers(context.headers)

        # Call the actual handler
        result = await update_task_handler(
            task_id=arguments["task_id"],
            user_id=user_id,
            title=arguments.get("title"),
            description=arguments.get("description"),
            status=arguments.get("status")
        )

        return ToolCallResult(
            content=[
                TextContent(
                    type="text",
                    text=json.dumps(result.dict())
                )
            ]
        )
    except Exception as e:
        error_result = ErrorResponse(
            success=False,
            error=str(e),
            error_code="UPDATE_TASK_ERROR"
        )
        return ToolCallResult(
            content=[
                TextContent(
                    type="text",
                    text=json.dumps(error_result.dict())
                )
            ]
        )

# Register the delete_task tool
@server.call_tool()
async def delete_task_tool(context, arguments: Dict[str, Any]) -> ToolCallResult:
    """
    Tool to delete a task for the authenticated user.

    Arguments:
    - task_id: The ID of the task to delete
    """
    try:
        # Extract user ID from context (headers)
        user_id = extract_user_id_from_headers(context.headers)

        # Call the actual handler
        result = await delete_task_handler(
            task_id=arguments["task_id"],
            user_id=user_id
        )

        return ToolCallResult(
            content=[
                TextContent(
                    type="text",
                    text=json.dumps(result.dict())
                )
            ]
        )
    except Exception as e:
        error_result = ErrorResponse(
            success=False,
            error=str(e),
            error_code="DELETE_TASK_ERROR"
        )
        return ToolCallResult(
            content=[
                TextContent(
                    type="text",
                    text=json.dumps(error_result.dict())
                )
            ]
        )

async def serve():
    """Start the MCP server."""
    async with server.serve():
        await asyncio.Event().wait()  # Keep the server running

if __name__ == "__main__":
    asyncio.run(serve())