"""
Custom exceptions for the FLAG CTF Framework.
"""
from typing import Optional, Dict, Any

class FlagError(Exception):
    """Base exception for the framework."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.details = details or {}

class ModuleNotFoundError(FlagError):
    """Raised when a specified module cannot be found."""
    pass

class ToolNotFoundError(FlagError):
    """Raised when an external tool is not installed or found."""
    pass

class InvalidOptionError(FlagError):
    """Raised when an invalid option is provided to a module or command."""
    pass

class ConfigError(FlagError):
    """Raised for configuration loading or parsing errors."""
    pass

class SessionError(FlagError):
    """Raised when session management fails."""
    pass

class PluginError(FlagError):
    """Raised when a plugin fails to load or execute."""
    pass

class ValidationError(FlagError):
    """Raised when input validation fails."""
    pass

class ExecutionError(FlagError):
    """Raised when command execution or a process fails."""
    pass
