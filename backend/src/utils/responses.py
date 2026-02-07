from typing import Any, Dict


def create_success_response(data: Any = None, message: str = "Success", status_code: int = 200) -> Dict[str, Any]:
    """
    Create a standardized success response
    """
    return {
        "status": "success",
        "status_code": status_code,
        "message": message,
        "data": data
    }


def create_error_response(error: str, message: str = "An error occurred", status_code: int = 400) -> Dict[str, Any]:
    """
    Create a standardized error response
    """
    return {
        "status": "error",
        "status_code": status_code,
        "message": message,
        "error": error
    }