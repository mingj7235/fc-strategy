class NexonAPIException(Exception):
    """Base exception for Nexon API errors"""
    pass


class UserNotFoundException(NexonAPIException):
    """Raised when user is not found"""
    pass


class MatchNotFoundException(NexonAPIException):
    """Raised when match is not found"""
    pass


class RateLimitException(NexonAPIException):
    """Raised when API rate limit is exceeded"""
    pass
