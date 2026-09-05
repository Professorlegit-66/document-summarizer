class AIServiceError(Exception):
    """Base exception for all AI service errors."""


class AIServiceUnavailableError(AIServiceError):
    """Raised when the AI service (e.g., Ollama) cannot be reached at all."""


class AIModelNotFoundError(AIServiceError):
    """Raised when the requested model is not available on the AI service."""


class AIRequestTimeoutError(AIServiceError):
    """Raised when a request to the AI service takes too long to respond."""


class AIResponseError(AIServiceError):
    """Raised when the AI service responds, but the response is invalid or unusable."""