"""
Base class for module categories in the CTF framework.
"""

from typing import Any
from core.base_tool import BaseTool

class BaseModule:
    """
    Base class representing a module category (e.g., Crypto, Pwn).
    """
    name: str = ''
    description: str = ''
    
    def __init__(self) -> None:
        """Initialize the base module and its tool registry."""
        self.tools: dict[str, type[BaseTool]] = {}
    
    def register_tool(self, tool_cls: type[BaseTool]) -> None:
        """
        Register a tool within this module.
        
        Args:
            tool_cls: The tool class to register.
        """
        self.tools[tool_cls.name] = tool_cls
    
    def get_tool(self, name: str) -> BaseTool | None:
        """
        Get an instantiated tool by name.
        
        Args:
            name: The name of the tool.
            
        Returns:
            An instance of the tool if found, None otherwise.
        """
        cls = self.tools.get(name)
        return cls() if cls else None
    
    def list_tools(self) -> list[dict]:
        """
        List all tools registered in this module.
        
        Returns:
            A list of dictionaries containing tool names and descriptions.
        """
        return [{'name': t.name, 'description': t.description} for t in self.tools.values()]
