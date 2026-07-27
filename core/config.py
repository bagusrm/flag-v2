"""
Configuration management for the FLAG CTF Framework.
"""
import yaml
from pathlib import Path
from typing import Any, Dict, Optional, Union
from .constants import CONFIG_FILE, VERSION, APP_NAME
from .exceptions import ConfigError

class Config:
    """Singleton configuration manager."""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, config_path: Union[str, Path] = CONFIG_FILE):
        if self._initialized:
            return
            
        self.config_path = Path(config_path)
        self.config_data: Dict[str, Any] = self._default_config()
        self.load()
        self._initialized = True

    def _default_config(self) -> Dict[str, Any]:
        """Provides default configuration."""
        return {
            'app': {
                'name': APP_NAME,
                'version': VERSION
            },
            'theme': 'dark',
            'log_level': 'INFO',
            'log_dir': 'logs',
            'session_dir': 'sessions',
            'history_size': 1000,
            'output_format': 'table',
            'colored_output': True,
            'auto_save_session': False,
            'plugin_dirs': ['modules', 'plugins']
        }

    def load(self) -> None:
        """Loads configuration from YAML file."""
        if not self.config_path.exists():
            # Apply defaults if file does not exist
            return
            
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if data:
                    self._merge_config(self.config_data, data)
        except yaml.YAMLError as e:
            raise ConfigError(f"Failed to parse config file: {e}")
        except Exception as e:
            raise ConfigError(f"Failed to read config file: {e}")

    def _merge_config(self, base: Dict[str, Any], override: Dict[str, Any]) -> None:
        """Deep merge two dictionaries."""
        for key, value in override.items():
            if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value

    def save(self) -> None:
        """Saves current configuration to YAML file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config_data, f, default_flow_style=False)
        except Exception as e:
            raise ConfigError(f"Failed to save config to {self.config_path}: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieves a config value, supporting dot notation for nested keys.
        Example: config.get('app.version')
        """
        keys = key.split('.')
        value = self.config_data
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any) -> None:
        """
        Sets a config value, supporting dot notation for nested keys.
        """
        keys = key.split('.')
        current = self.config_data
        for k in keys[:-1]:
            if k not in current or not isinstance(current[k], dict):
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value

    @classmethod
    def get_instance(cls, config_path: Union[str, Path] = CONFIG_FILE) -> 'Config':
        """Get or create the singleton Config instance."""
        if cls._instance is None:
            return cls(config_path)
        return cls._instance

    def reload(self) -> None:
        """Reloads the configuration from file."""
        self.config_data = self._default_config()
        self.load()
