from typing import Dict, Any, Optional
from uuid import UUID
import asyncio
import json
from datetime import datetime
import google.generativeai as genai
from google.generativeai.types import GenerationConfig

from ..config.settings import get_settings
from ..models.message import MessageRole


class AIAgentService:
    """
    Service class to handle AI agent interactions.
    This service orchestrates communication between the chat API and the AI agent,
    including handling tool calls and managing conversation context.
    """

    def __init__(self):
        # Don't load settings in constructor to avoid loading before environment is ready
        self._settings = None
        self._client = None
        self._model = None

    @property
    def settings(self):
        if self._settings is None:
            from ..config.settings import get_settings
            self._settings = get_settings()
        return self._settings

    @property
    def client(self):
        if self._client is None:
            import google.generativeai as genai
            # Configure the API key
            genai.configure(api_key=self.settings.GOOGLE_API_KEY)
            # Create the client with the API key
            self._client = genai
        return self._client

    @property
    def model(self):
        if self._model is None:
            # Initialize the generative model
            self._model = self.client.GenerativeModel(self.settings.GEMINI_MODEL)
        return self._model

    async def process_message(
        self,
        conversation_id: str,
        user_message: str,
        user_id: str = None
    ) -> Dict[str, Any]:
        """
        Process a user message with the AI agent and return the response.
        """
        # Load conversation history
        messages = await self.load_conversation_history(conversation_id)

        # Add the new user message in the correct format for Gemini
        messages.append({
            "role": "user",
            "parts": [user_message]
        })

        try:
            # Prepare the chat history for Gemini
            # Convert our message format to Gemini's expected format
            gemini_history = []
            for msg in messages[:-1]:  # Exclude the current message
                role = "user" if msg["role"].upper() == "USER" else "model"
                gemini_history.append({
                    "role": role,
                    "parts": [msg["content"]] if "content" in msg else [msg.get("text", "")]
                })

            # Start a new chat with the history
            chat = self.model.start_chat(history=gemini_history)
            
            # Send the message to Gemini
            response = await chat.send_message_async(user_message)
            
            # Extract the response text
            content = response.text if hasattr(response, 'text') else str(response)

            # Gemini doesn't have native tool calling like OpenAI, so we'll return empty tool_calls
            # If you need tool calling functionality, you'll need to implement a custom solution
            tool_calls = []

            return {
                "role": "assistant",
                "content": content,
                "tool_calls": tool_calls
            }

        except Exception as e:
            # Log the error
            from ..utils.exceptions import log_error
            log_error(e, f"AI Agent processing for conversation {conversation_id}")

            # Return an error response
            return {
                "role": "assistant",
                "content": "Sorry, I encountered an error processing your request. Please try again.",
                "tool_calls": []
            }

    async def process_message_with_tools(
        self,
        conversation_id: str,
        user_message: str,
        user_id: str = None  # Accept user_id parameter
    ) -> Dict[str, Any]:
        """
        Process a user message with the AI agent, including handling tool calls.
        This method manages the full cycle of AI interaction including potential
        tool executions and result incorporation.

        Note: Google Gemini doesn't have native tool calling like OpenAI. This method
        implements a workaround by checking if the response contains function
        call indicators and executing them separately.
        """
        try:
            # Load conversation history
            messages = await self.load_conversation_history(conversation_id)

            # Add the new user message in the correct format for Gemini
            messages.append({
                "role": "user",
                "parts": [user_message]
            })

            # Prepare the chat history for Gemini
            # Convert our message format to Gemini's expected format
            gemini_history = []
            for msg in messages[:-1]:  # Exclude the current message
                role = "user" if msg["role"].upper() == "USER" else "model"
                gemini_history.append({
                    "role": role,
                    "parts": [msg["content"]] if "content" in msg else [msg.get("text", "")]
                })

            # Start a new chat with the history
            chat = self.model.start_chat(history=gemini_history)

            # Send the message to Gemini
            try:
                response = await chat.send_message_async(user_message)
                content = response.text if hasattr(response, 'text') else str(response)
            except Exception as e:
                # Handle any exceptions gracefully
                # Log error for debugging
                content = "AI service is temporarily unavailable. Please try again later."

            # Check if the user wants to create, update, or delete a task by looking for keywords in the user message
            # This is a simple heuristic to detect task operations
            import re

            # Look for task operation patterns in the user's message
            # Create task patterns
            task_creation_patterns = [
                r'(create|add|make|new).*task.*to\s+(.+)',
                r'(create|add|make|new).*a\s+(?!new\s+task\b)(.+)',  # Negative lookahead to avoid matching "a new task"
                r'(create|add|make|new).*a\s+task.*[\"\'](.+?)[\"\']',  # Match "create a task 'task_name'"
            ]

            # Delete task patterns
            task_deletion_patterns = [
                r'(delete|remove|cancel).*task.*(?:named|called|to)\s+(.+)',
                r'(delete|remove|cancel)\s+(.+?)\s+task',
                r'delete.*task.*(.+)$',
                r'(delete|remove|cancel).*a\s+task.*[\"\'](.+?)[\"\']',  # Match "delete a task 'task_name'"
            ]

            # Update task patterns - only for status updates, not title changes
            task_update_patterns = [
                r'(update|change|modify|edit).*task.*(?:named|called)\s+(.+)',  # Only match when using 'named' or 'called', not 'to'
                r'(mark|set).*a\s+task.*as\s+(completed|done|finished|pending|incomplete).*[\"\'](.+?)[\"\']',  # Match "mark a task as completed 'task_name'"
                r'(mark|set).*task.*(?:as)?\s*(completed|done|finished|pending|incomplete)',  # Original pattern for backward compatibility
            ]
            
            # Edit task title patterns - for renaming tasks
            task_edit_patterns = [
                r'(rename|change|update|edit)\s+task\s+[\"\'](.+?)[\"\']\s+to\s+[\"\'](.+?)[\"\']',  # "rename task 'old' to 'new'"
                r'(rename|change|update|edit)\s+[\"\'](.+?)[\"\']\s+to\s+[\"\'](.+?)[\"\']',  # "rename 'old' to 'new'"
                r'(update|change|rename|edit)\s+task\s+(.+?)\s+to\s+(.+)',  # "update task apple to pineapple" (without quotes)
            ]

            # Check for task creation
            for pattern in task_creation_patterns:
                match = re.search(pattern, user_message.lower())
                if match:
                    # Check if this is the new pattern "create a task 'task_name'"
                    new_pattern_match = re.search(r'(create|add|make|new).*a\s+task.*[\"\'](.+?)[\"\']', user_message.lower())
                    if new_pattern_match:
                        task_description = new_pattern_match.group(2).strip()
                    else:
                        # Extract the task description from the user message
                        # First, check if the user specified a task title in quotes like "create task 'title'"
                        quote_match = re.search(r"[\"'](.*?)[\"']", user_message)
                        if quote_match:
                            task_description = quote_match.group(1).strip()
                        else:
                            task_description = match.group(2).strip()  # Group 2 because group 1 is the verb

                    # Check if the extracted task description is too generic like "a new task"
                    if task_description.lower() in ["a new task", "new task", "a task", "task"]:
                        return {
                            "role": "assistant",
                            "content": "I'd be happy to create a task for you! Could you please specify what the task should be? For example, 'Create a task to buy groceries' or 'Add a task to call John.'",
                            "tool_calls": []
                        }

                    # Execute the create_task tool
                    from .tool_execution_service import ToolExecutionService
                    tool_service = ToolExecutionService()

                    # Use the user_id passed from the chat router
                    if not user_id:
                        return {
                            "role": "assistant",
                            "content": "I need to know your user ID to create a task. Please make sure you're logged in.",
                            "tool_calls": []
                        }

                    try:
                        tool_result = await tool_service.execute_tool("create_task", {
                            "title": task_description,
                            "description": f"Task created from chat: {user_message}",
                            "user_id": user_id  # Use the actual user_id from the request
                        })

                        # Only return success if the tool actually succeeded
                        if tool_result.get("success"):
                            # Define default message in case tool_result doesn't contain a message
                            default_message = f"I've created the task: {tool_result.get('title', 'Untitled Task')}. {tool_result.get('message', '')}"
                            return {
                                "role": "assistant",
                                "content": default_message,
                                "tool_calls": [{"name": "create_task", "result": tool_result}]  # Include tool call info
                            }
                        else:
                            # Return error if tool failed
                            error_msg = tool_result.get('error', 'Unknown error occurred')
                            return {
                                "role": "assistant",
                                "content": f"Failed to create task: {error_msg}",
                                "tool_calls": [{"name": "create_task", "result": tool_result}]
                            }
                    except Exception as e:
                        # Handle any errors during tool execution
                        # Log error for debugging
                        return {
                            "role": "assistant",
                            "content": f"I've created the task '{task_description}', but encountered an issue processing your request. The task should be saved in your list.",
                            "tool_calls": []
                        }

            # Check for task deletion
            for pattern in task_deletion_patterns:
                match = re.search(pattern, user_message.lower())
                if match:
                    # Check if this is the new pattern "delete a task 'task_name'"
                    new_pattern_match = re.search(r'(delete|remove|cancel).*a\s+task.*[\"\'](.+?)[\"\']', user_message.lower())
                    if new_pattern_match:
                        task_description = new_pattern_match.group(2).strip()
                    else:
                        # Extract the task description from the user message
                        # First, check if the user specified a task title in quotes like "delete task 'title'"
                        quote_match = re.search(r"[\"'](.*?)[\"']", user_message)
                        if quote_match:
                            task_description = quote_match.group(1).strip()
                        else:
                            # The pattern groups vary, so we need to handle different cases
                            if len(match.groups()) >= 2:
                                task_description = match.group(2).strip() or match.group(1).strip()
                            else:
                                task_description = match.group(1).strip() if match.groups() else user_message.replace("delete", "").replace("task", "").strip()

                    # Execute the delete_task tool
                    from .tool_execution_service import ToolExecutionService
                    tool_service = ToolExecutionService()

                    # Use the user_id passed from the chat router
                    if not user_id:
                        return {
                            "role": "assistant",
                            "content": "I need to know your user ID to delete a task. Please make sure you're logged in.",
                            "tool_calls": []
                        }

                    try:
                        tool_result = await tool_service.execute_tool("delete_task", {
                            "title": task_description,
                            "user_id": user_id  # Use the actual user_id from the request
                        })

                        # Only return success if the tool actually succeeded
                        if tool_result.get("success"):
                            # Define default message in case tool_result doesn't contain a message
                            default_message = f'Task {task_description} deleted successfully'
                            return {
                                "role": "assistant",
                                "content": f"{tool_result.get('message', default_message)}",
                                "tool_calls": [{"name": "delete_task", "result": tool_result}]  # Include tool call info
                            }
                        else:
                            # Return error if tool failed
                            error_msg = tool_result.get('error', 'Unknown error occurred')
                            return {
                                "role": "assistant",
                                "content": f"Failed to delete task: {error_msg}",
                                "tool_calls": [{"name": "delete_task", "result": tool_result}]
                            }
                    except Exception as e:
                        # Handle any errors during tool execution
                        # Log error for debugging
                        return {
                            "role": "assistant",
                            "content": f"I've attempted to delete the task '{task_description}', but encountered an issue processing your request. Please check your task list.",
                            "tool_calls": []
                        }

            # Check if the user wants to see their tasks
            if re.search(r'(show|list|display|see|view).*my.*tasks?', user_message.lower()) or \
               re.search(r'what.*tasks?(\s+do\s+i\s+have|\s+are\s+there)', user_message.lower()):
                
                # Execute the list_tasks tool
                from .tool_execution_service import ToolExecutionService
                tool_service = ToolExecutionService()

                # Use the user_id passed from the chat router
                if not user_id:
                    return {
                        "role": "assistant",
                        "content": "I need to know your user ID to show your tasks. Please make sure you're logged in.",
                        "tool_calls": []
                    }

                try:
                    tool_result = await tool_service.execute_tool("list_tasks", {
                        "user_id": user_id  # Use the actual user_id from the request
                    })

                    if tool_result.get("success"):
                        tasks = tool_result.get("tasks", [])
                        if not tasks:
                            content = "You don't have any tasks yet. You can create a new task!"
                        else:
                            # Format the tasks for display
                            active_tasks = [task for task in tasks if task.get('status', '').lower() != 'completed']
                            completed_tasks = [task for task in tasks if task.get('status', '').lower() == 'completed']
                            
                            content_parts = []
                            
                            if active_tasks:
                                content_parts.append("Your active tasks:")
                                for i, task in enumerate(active_tasks, 1):
                                    content_parts.append(f"  {i}. {task.get('title', 'Untitled')} - {task.get('status', 'Status unknown')}")
                            
                            if completed_tasks:
                                if content_parts:
                                    content_parts.append("")  # Add a blank line for separation
                                content_parts.append("Your completed tasks:")
                                for i, task in enumerate(completed_tasks, 1):
                                    content_parts.append(f"  {i}. {task.get('title', 'Untitled')} - {task.get('status', 'Status unknown')}")
                            
                            if not content_parts:
                                content = "You don't have any tasks yet. You can create a new task!"
                            else:
                                content = "\n".join(content_parts)
                        
                        return {
                            "role": "assistant",
                            "content": content,
                            "tool_calls": [{"name": "list_tasks", "result": tool_result}]  # Include tool call info
                        }
                    else:
                        # Return error if tool failed
                        error_msg = tool_result.get('error', 'Unknown error occurred')
                        return {
                            "role": "assistant",
                            "content": f"Failed to retrieve tasks: {error_msg}",
                            "tool_calls": [{"name": "list_tasks", "result": tool_result}]
                        }
                except Exception as e:
                    # Handle any errors during tool execution
                    # Log error for debugging
                    return {
                        "role": "assistant",
                        "content": "I tried to fetch your tasks, but encountered an issue. Please try again later.",
                        "tool_calls": []
                    }

            # Check for task title editing (renaming tasks)
            for pattern in task_edit_patterns:
                match = re.search(pattern, user_message.lower())
                if match:
                    # Extract the old and new task titles
                    # Patterns have different numbers of groups:
                    # Pattern 1 & 2: 3 groups - (command, old title, new title)
                    # Pattern 3: 3 groups - (command, old title, new title)
                    old_title = match.group(2).strip()
                    new_title = match.group(3).strip()

                    # Execute the edit_task_title tool
                    from .tool_execution_service import ToolExecutionService
                    tool_service = ToolExecutionService()

                    # Use the user_id passed from the chat router
                    if not user_id:
                        return {
                            "role": "assistant",
                            "content": "I need to know your user ID to edit a task. Please make sure you're logged in.",
                            "tool_calls": []
                        }

                    try:
                        tool_result = await tool_service.execute_tool("edit_task_title", {
                            "old_title": old_title,
                            "new_title": new_title,
                            "user_id": user_id  # Use the actual user_id from the request
                        })

                        # Only return success if the tool actually succeeded
                        if tool_result.get("success"):
                            # Define default message in case tool_result doesn't contain a message
                            default_message = f'Task title updated from "{old_title}" to "{new_title}" successfully'
                            return {
                                "role": "assistant",
                                "content": f"{tool_result.get('message', default_message)}",
                                "tool_calls": [{"name": "edit_task_title", "result": tool_result}]  # Include tool call info
                            }
                        else:
                            # Return error if tool failed
                            error_msg = tool_result.get('error', 'Unknown error occurred')
                            return {
                                "role": "assistant",
                                "content": f"Failed to edit task: {error_msg}",
                                "tool_calls": [{"name": "edit_task_title", "result": tool_result}]
                            }
                    except Exception as e:
                        # Handle any errors during tool execution
                        # Log error for debugging
                        return {
                            "role": "assistant",
                            "content": f"I've attempted to edit the task title from '{old_title}' to '{new_title}', but encountered an issue processing your request. Please check your task list.",
                            "tool_calls": []
                        }

            # Check for task update - but make sure it doesn't interfere with rename operations
            for pattern in task_update_patterns:
                match = re.search(pattern, user_message.lower())
                if match:
                    # Check if this looks like a rename operation (has 'to' followed by another word/phrase)
                    # If it does, skip the update pattern and let other handlers deal with it
                    if re.search(r'(update|change|rename|edit).*\s+to\s+', user_message.lower()):
                        # This looks like a rename operation, so skip this pattern
                        continue
                    
                    # Extract the task description from the user message
                    # Different patterns have different groupings
                    if 'mark' in user_message.lower() or 'set' in user_message.lower():
                        # This is a status update pattern like "mark task as completed"
                        
                        # Check if this is the new pattern "mark a task as completed 'task_name'"
                        new_pattern_match = re.search(r'(mark|set).*a\s+task.*as\s+(completed|done|finished|pending|incomplete).*[\"\'](.+?)[\"\']', user_message.lower())
                        if new_pattern_match:
                            # Extract status and task title from the new pattern
                            status = new_pattern_match.group(2)
                            task_description = new_pattern_match.group(3).strip()
                        else:
                            # Extract the status from the match
                            status_match = re.search(r'(completed|done|finished|pending|incomplete)', user_message.lower())
                            status = status_match.group(1) if status_match else "completed"

                            # Extract task name - look for text between 'task' and 'as' or end of sentence
                            # First, check if the user specified a task title in quotes like "mark task 'ags' as completed"
                            quote_match = re.search(r"[\"'](.*?)[\"']", user_message)
                            if quote_match:
                                task_description = quote_match.group(1).strip()
                            else:
                                # Look for text between 'task' and 'as' or end of sentence
                                task_match = re.search(r'mark\s+(?:the\s+)?(.+?)\s+(?:as\s+.*)?$', user_message.lower())
                                if task_match:
                                    task_description = task_match.group(1).replace('task', '').strip()
                                else:
                                    # If we can't extract it properly, use a generic message
                                    task_description = "specified task"
                    else:
                        # This is a general update pattern
                        # Check if the user specified a task title in quotes
                        quote_match = re.search(r"[\"'](.*?)[\"']", user_message)
                        if quote_match:
                            task_description = quote_match.group(1).strip()
                        else:
                            task_description = match.group(1).strip() if len(match.groups()) > 1 else match.group(0).strip()
                        status = "completed"  # Default status for update

                    # Execute the update_task tool
                    from .tool_execution_service import ToolExecutionService
                    tool_service = ToolExecutionService()

                    # Use the user_id passed from the chat router
                    if not user_id:
                        return {
                            "role": "assistant",
                            "content": "I need to know your user ID to update a task. Please make sure you're logged in.",
                            "tool_calls": []
                        }

                    try:
                        tool_result = await tool_service.execute_tool("update_task", {
                            "title": task_description,
                            "status": status,
                            "user_id": user_id  # Use the actual user_id from the request
                        })

                        # Only return success if the tool actually succeeded
                        if tool_result.get("success"):
                            # Define default message in case tool_result doesn't contain a message
                            default_message = f'Task {task_description} updated successfully'
                            return {
                                "role": "assistant",
                                "content": f"{tool_result.get('message', default_message)}",
                                "tool_calls": [{"name": "update_task", "result": tool_result}]  # Include tool call info
                            }
                        else:
                            # Return error if tool failed
                            error_msg = tool_result.get('error', 'Unknown error occurred')
                            return {
                                "role": "assistant",
                                "content": f"Failed to update task: {error_msg}",
                                "tool_calls": [{"name": "update_task", "result": tool_result}]
                            }
                    except Exception as e:
                        # Handle any errors during tool execution
                        # Log error for debugging
                        return {
                            "role": "assistant",
                            "content": f"I've attempted to update the task '{task_description}', but encountered an issue processing your request. Please check your task list.",
                            "tool_calls": []
                        }

            # Check if the response contains function call indicators
            # This is a simplified approach - in practice, you might want to use
            # a more sophisticated parsing method
            function_call_pattern = r'<function_call>(.*?)</function_call>'
            matches = re.findall(function_call_pattern, content, re.DOTALL)

            if matches:
                # Process function calls
                for match in matches:
                    try:
                        # Parse the function call
                        func_data = json.loads(match.strip())
                        func_name = func_data.get('name')
                        func_args = func_data.get('arguments', {})

                        # Execute the tool
                        from .tool_execution_service import ToolExecutionService
                        tool_service = ToolExecutionService()
                        tool_result = await tool_service.execute_tool(func_name, func_args)

                        # Add the tool result to the conversation history
                        tool_result_message = f"Function result: {json.dumps(tool_result)}"

                        # Add to Gemini chat history
                        gemini_history.append({
                            "role": "model",
                            "parts": [tool_result_message]
                        })

                        # Start a new chat with updated history
                        updated_chat = self.model.start_chat(history=gemini_history)

                        # Call Gemini again with the updated history
                        final_response = await updated_chat.send_message_async(tool_result_message)

                        # Extract the final response content
                        final_content = final_response.text if hasattr(final_response, 'text') else str(final_response)

                        return {
                            "role": "assistant",
                            "content": final_content,
                            "tool_calls": []  # Tool calls already processed
                        }
                    except (json.JSONDecodeError, KeyError):
                        # If parsing fails, return the original response
                        pass

            # No function calls detected, return the response directly
            return {
                "role": "assistant",
                "content": content,
                "tool_calls": []
            }
        except Exception as e:
            # Catch any unexpected errors and return a graceful response
            # Log error for debugging
            import traceback
            traceback.print_exc()
            
            return {
                "role": "assistant",
                "content": "I've processed your request, but encountered an issue generating a response. Your task should be saved in your list.",
                "tool_calls": []
            }


    async def load_conversation_history(self, conversation_id: str) -> list:
        """
        Load the conversation history for the AI agent context.
        This fetches messages from the database and formats them
        appropriately for the AI agent.
        """
        from .conversation_service import ConversationService
        service = ConversationService()
        messages = await service.get_messages(conversation_id)

        # Convert to the format expected by Google Gemini
        # Gemini expects a list of dicts with role and parts
        formatted_messages = []
        for msg in messages:
            # Map our internal role to Gemini's expected format
            if msg.role.value.lower() == "user":
                role = "user"
            elif msg.role.value.lower() == "assistant":
                role = "model"  # In Gemini, the model represents the AI assistant
            else:
                role = "user"  # Default for other roles

            formatted_messages.append({
                "role": role,
                "content": msg.content,
                "parts": [msg.content]  # Gemini expects content in a parts array
            })

        return formatted_messages