"""
Plugin and module manager for dynamic loading in the CTF framework.
"""

import importlib
import importlib.util
from pathlib import Path
import sys
import logging
from typing import List

from core.registry import ModuleRegistry
from core.config import Config
from core.base_tool import get_registered_tools, clear_registered_tools
from core.logger import get_logger

class PluginManager:
    """
    Manager responsible for discovering and loading modules and plugins.
    """
    
    def __init__(self, registry: ModuleRegistry, config: Config) -> None:
        """
        Initialize the PluginManager.
        
        Args:
            registry: The central module registry.
            config: The application configuration.
        """
        self.registry = registry
        self.config = config
        self.logger = get_logger("PluginManager")
        self._loaded_paths: List[str] = []

    def discover_modules(self, paths: list[str]) -> int:
        """
        Discover and register tools from given paths.
        
        Args:
            paths: List of directory paths to scan.
            
        Returns:
            Count of newly loaded tools.
        """
        total_loaded = 0
        for path_str in paths:
            base_path = Path(path_str)
            if not base_path.exists() or not base_path.is_dir():
                self.logger.warning(f"Path does not exist or is not a directory: {base_path}")
                continue
                
            if path_str not in self._loaded_paths:
                self._loaded_paths.append(path_str)
            
            for sub_path in base_path.iterdir():
                if sub_path.is_dir() and sub_path.name != "__pycache__" and not sub_path.name.startswith("_"):
                    for py_file in sub_path.rglob("*.py"):
                        if py_file.name.startswith("_"):
                            continue
                        loaded_count = self.load_module_file(py_file)
                        total_loaded += loaded_count
        
        return total_loaded

    def load_module_file(self, filepath: Path) -> int:
        """
        Dynamically load a Python file and register its tools.
        
        Args:
            filepath: Path to the python file.
            
        Returns:
            Count of loaded tools from the file.
        """
        module_name = filepath.stem
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        
        if spec is None or spec.loader is None:
            self.logger.error(f"Could not load spec for {filepath}")
            return 0
            
        clear_registered_tools()
        
        try:
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
        except Exception as e:
            self.logger.error(f"Error executing module {filepath}: {e}")
            return 0
            
        tools = get_registered_tools()
        for tool_cls in tools:
            self.registry.register_tool(tool_cls)
            
        clear_registered_tools()
        return len(tools)

    def reload_all(self) -> int:
        """
        Reload all previously loaded module paths.
        
        Returns:
            Count of reloaded tools.
        """
        # A simple approach to reload by re-discovering
        return self.discover_modules(self._loaded_paths)
