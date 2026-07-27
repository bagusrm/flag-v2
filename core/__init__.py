"""
Core package for the FLAG CTF Framework.
"""
from .constants import VERSION, APP_NAME, FULL_NAME, AUTHOR, BANNER
from .config import Config
from .logger import get_logger

try:
    from .app import FlagApp
except ImportError:
    # FlagApp might not be implemented yet
    pass

__all__ = ['Config', 'get_logger', 'VERSION', 'APP_NAME', 'FULL_NAME', 'AUTHOR', 'BANNER']
