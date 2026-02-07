class ValidationError(Exception):
    """
    Exception raised for validation errors
    """
    def __init__(self, message: str = "Validation error occurred"):
        self.message = message
        super().__init__(self.message)


class NotFoundError(Exception):
    """
    Exception raised when a resource is not found
    """
    def __init__(self, message: str = "Resource not found"):
        self.message = message
        super().__init__(self.message)


class UnauthorizedError(Exception):
    """
    Exception raised when access is unauthorized
    """
    def __init__(self, message: str = "Unauthorized access"):
        self.message = message
        super().__init__(self.message)


class ForbiddenError(Exception):
    """
    Exception raised when access is forbidden
    """
    def __init__(self, message: str = "Access forbidden"):
        self.message = message
        super().__init__(self.message)


class ConflictError(Exception):
    """
    Exception raised when there's a conflict in the request
    """
    def __init__(self, message: str = "Conflict in request"):
        self.message = message
        super().__init__(self.message)