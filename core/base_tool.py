"""
Abstract base class for all tools in the CTF framework.
Every tool must extend this base class to ensure consistent behavior and API.
"""

from abc import ABC, abstractmethod
from typing import Any
from dataclasses import dataclass, field

from core.exceptions import InvalidOptionError, ValidationError


@dataclass
class ToolOption:
    """
    Represents a single tool option/parameter.
    
    Attributes:
        name: The name of the option.
        description: A brief description of what the option does.
        required: Whether the option must be provided.
        default: The default value if not provided.
        value: The current value set by the user.
        choices: Optional list of allowed values.
    """
    name: str
    description: str
    required: bool = False
    default: Any = None
    value: Any = None
    choices: list[str] | None = None
    
    @property
    def display_value(self) -> str:
        """Returns the string representation of the current or default value."""
        if self.value is not None:
            return str(self.value)
        if self.default is not None:
            return str(self.default)
        return ''
    
    @property 
    def current_value(self) -> Any:
        """Returns the value or default value."""
        return self.value if self.value is not None else self.default


class BaseTool(ABC):
    """
    Abstract base class for all tools.
    """
    # Class-level metadata
    name: str = ''
    category: str = ''
    description: str = ''
    author: str = 'CTF Team'
    version: str = '1.0.0'
    references: list[str] = []
    tags: list[str] = []
    
    def __init__(self):
        """Initialize the tool and set up options."""
        self._options: dict[str, ToolOption] = {}
        self._setup_options()
    
    def _setup_options(self) -> None:
        """
        Override this method to define tool options.
        Call self.add_option() within this method to register options.
        """
        pass
    
    def add_option(self, name: str, description: str, required: bool = False, default: Any = None, choices: list[str] | None = None) -> None:
        """
        Add an option to the tool.
        
        Args:
            name: The option name.
            description: What the option does.
            required: If the option is mandatory.
            default: Default value.
            choices: List of valid values.
        """
        self._options[name.upper()] = ToolOption(
            name=name.upper(), description=description,
            required=required, default=default, choices=choices
        )
    
    def set_option(self, name: str, value: Any) -> None:
        """
        Set the value of an option with instant path validation if applicable.
        
        Args:
            name: The name of the option to set.
            value: The value to assign to the option.
            
        Raises:
            InvalidOptionError: If the option is unknown or the value is invalid.
        """
        key = name.upper()
        if key not in self._options:
            raise InvalidOptionError(f'Unknown option: {name}')
        opt = self._options[key]
        if opt.choices and value not in opt.choices:
            raise InvalidOptionError(f'{name} must be one of: {opt.choices}')
            
        # Universal file/path existence check for path-like values or path option names
        val_str = str(value).strip()
        is_path_option = any(p in key for p in ['FILE', 'PATH', 'DIR', 'INPUT', 'OUTPUT', 'SCRIPT', 'BINARY'])
        is_path_like = val_str.startswith(('/', './', '../', '~/')) or (len(val_str) > 2 and val_str[1:3] in [':\\', ':/'])
        
        if (is_path_option or is_path_like) and val_str:
            from pathlib import Path
            try:
                val_path = Path(val_str).expanduser().resolve()
                # For output files, check parent directory instead of file itself
                if 'OUTPUT' in key:
                    if not val_path.parent.exists():
                        raise InvalidOptionError(f"Directory not found for output: '{val_path.parent}'")
                else:
                    if not val_path.exists():
                        raise InvalidOptionError(f"File/Path not found: '{val_str}' (Resolved: {val_path})")
                value = str(val_path)
            except Exception as e:
                if isinstance(e, InvalidOptionError):
                    raise e
                pass
            
        opt.value = value
    
    def get_option(self, name: str) -> Any:
        """
        Get the current value of an option.
        
        Args:
            name: The name of the option.
            
        Returns:
            The value or default value of the option.
            
        Raises:
            InvalidOptionError: If the option does not exist.
        """
        key = name.upper()
        if key not in self._options:
            raise InvalidOptionError(f'Unknown option: {name}')
        return self._options[key].current_value
    
    @property
    def options(self) -> dict[str, ToolOption]:
        """Returns the dictionary of defined options."""
        return self._options
    
    def validate(self) -> bool:
        """
        Validate all required options have been set.
        
        Returns:
            True if valid.
            
        Raises:
            ValidationError: If any required option is missing.
        """
        for opt in self._options.values():
            if opt.required and opt.current_value is None:
                raise ValidationError(f'Required option not set: {opt.name}')
        return True
    
    @abstractmethod
    def run(self) -> dict[str, Any]:
        """
        Execute the core logic of the tool.
        
        Returns:
            A dictionary containing at least 'status' and 'result' keys.
        """
        ...
    
    def execute(self) -> dict[str, Any]:
        """
        Validate options and then run the tool.
        
        Returns:
            The execution results from run().
        """
        self.validate()
        return self.run()
    
    def get_info(self) -> dict:
        """
        Get metadata about the tool.
        
        Returns:
            Dictionary containing tool metadata.
        """
        return {
            'name': self.name, 'category': self.category,
            'description': self.description, 'author': self.author,
            'version': self.version, 'references': self.references,
            'tags': self.tags,
        }
    
    def reset(self) -> None:
        """Reset all option values to their defaults (None)."""
        for opt in self._options.values():
            opt.value = None
    
    @property
    def full_name(self) -> str:
        """Returns the full name of the tool, including category."""
        return f'{self.category}/{self.name}'


# Tool registration via decorator
_tool_registry: list[type[BaseTool]] = []

def register_tool(cls: type[BaseTool]) -> type[BaseTool]:
    """
    Decorator to register a tool class in the global registry.
    
    Args:
        cls: The tool class to register.
        
    Returns:
        The tool class.
    """
    _tool_registry.append(cls)
    return cls

def get_registered_tools() -> list[type[BaseTool]]:
    """
    Retrieve all registered tools.
    
    Returns:
        List of tool classes.
    """
    return list(_tool_registry)

def clear_registered_tools() -> None:
    """Clear all registered tools."""
    _tool_registry.clear()
