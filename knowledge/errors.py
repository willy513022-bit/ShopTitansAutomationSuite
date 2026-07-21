class KnowledgeBaseError(Exception):
    """Base exception for knowledge-base failures."""


class KnowledgeValidationError(KnowledgeBaseError):
    """Raised when a knowledge document does not match its required structure."""
