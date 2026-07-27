"""
Singleton module and tool registry for the CTF framework.
"""

from typing import Any
from core.base_tool import BaseTool
from core.base_module import BaseModule

class ModuleRegistry:
    """
    Singleton registry to hold all categories and tools.
    """
    _instance: 'ModuleRegistry | None' = None

    def __new__(cls) -> 'ModuleRegistry':
        if cls._instance is None:
            cls._instance = super(ModuleRegistry, cls).__new__(cls)
            cls._instance._categories = {}
            cls._instance._tools = {}
        return cls._instance

    def __init__(self) -> None:
        """Initialize the module registry."""
        # Note: Initialization is handled in __new__ for the singleton.
        pass

    @classmethod
    def get_instance(cls) -> 'ModuleRegistry':
        """Get or create the singleton ModuleRegistry instance."""
        if cls._instance is None:
            return cls()
        return cls._instance

    @property
    def _categories(self) -> dict[str, BaseModule]:
        return getattr(self, '__categories', {})

    @_categories.setter
    def _categories(self, value: dict[str, BaseModule]) -> None:
        setattr(self, '__categories', value)

    @property
    def _tools(self) -> dict[str, dict[str, type[BaseTool]]]:
        return getattr(self, '__tools', {})

    @_tools.setter
    def _tools(self, value: dict[str, dict[str, type[BaseTool]]]) -> None:
        setattr(self, '__tools', value)

    def register_tool(self, tool_cls: type[BaseTool]) -> None:
        """
        Register a tool by its category.
        
        Args:
            tool_cls: The tool class to register.
        """
        category = tool_cls.category
        if not category:
            category = "misc"

        if category not in self._tools:
            self._tools[category] = {}
            
        self._tools[category][tool_cls.name] = tool_cls
        
        if category not in self._categories:
            mod = BaseModule()
            mod.name = category
            self._categories[category] = mod
            
        self._categories[category].register_tool(tool_cls)

    def get_tool(self, category: str, name: str) -> BaseTool | None:
        """
        Get an instantiated tool by category and name.
        
        Args:
            category: The category of the tool.
            name: The name of the tool.
            
        Returns:
            An instance of the tool if found, None otherwise.
        """
        cat_dict = self._tools.get(category)
        if cat_dict:
            cls = cat_dict.get(name)
            if cls:
                return cls()
        return None

    def get_category_tools(self, category: str) -> list[dict]:
        """
        Get all tools in a specific category.
        
        Args:
            category: The category to retrieve tools from.
            
        Returns:
            List of dictionaries containing tool information.
        """
        cat_dict = self._tools.get(category, {})
        info_list = []
        for cls in cat_dict.values():
            info_list.append(cls().get_info())
        return info_list

    def get_all_categories(self) -> list[dict]:
        """
        Get all registered categories.
        
        Returns:
            List of dictionaries containing category names, descriptions, and tool count.
        """
        from core.constants import CATEGORY_DESCRIPTIONS
        results = []
        for cat in self._categories.values():
            desc = cat.description or CATEGORY_DESCRIPTIONS.get(cat.name, '')
            tool_count = len(self._tools.get(cat.name, {}))
            results.append({
                'name': cat.name,
                'description': desc,
                'tool_count': tool_count
            })
        return results

    def search(self, keyword: str) -> list[dict]:
        """
        Search for tools matching a keyword.
        
        Args:
            keyword: The search term (checks name, description, tags).
            
        Returns:
            List of dictionaries containing matching tool information.
        """
        keyword_lower = keyword.lower()
        results = []
        for cat_dict in self._tools.values():
            for tool_cls in cat_dict.values():
                tool_instance = tool_cls()
                info = tool_instance.get_info()
                
                name = info.get('name', '').lower()
                desc = info.get('description', '').lower()
                tags = [t.lower() for t in info.get('tags', [])]
                
                if keyword_lower in name or keyword_lower in desc or any(keyword_lower in t for t in tags):
                    results.append(info)
        return results

    def get_all_tools(self) -> list[dict]:
        """
        Get all registered tools across all categories.
        
        Returns:
            List of dictionaries containing tool information.
        """
        results = []
        for cat_dict in self._tools.values():
            for tool_cls in cat_dict.values():
                results.append(tool_cls().get_info())
        return results

    @property
    def tool_count(self) -> int:
        """Returns the total number of registered tools."""
        return sum(len(cat) for cat in self._tools.values())

    @property
    def category_count(self) -> int:
        """Returns the total number of registered categories."""
        return len(self._tools)
