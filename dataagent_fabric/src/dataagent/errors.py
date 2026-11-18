"""Typed application errors safe to map to user-facing messages."""


class DataAgentError(Exception):
    """Base class for expected application failures."""


class ConfigurationError(DataAgentError):
    """Configuration is missing or inconsistent."""


class AuthenticationError(DataAgentError):
    """Microsoft Entra authentication failed."""


class PermissionDeniedError(DataAgentError):
    """The identity lacks tenant, workspace, or semantic-model access."""


class QueryValidationError(DataAgentError):
    """A logical query plan violates the catalog or safety policy."""


class SemanticModelError(DataAgentError):
    """The semantic-model API rejected or could not execute a query."""


class LLMError(DataAgentError):
    """Gemini could not plan or summarize the request."""
