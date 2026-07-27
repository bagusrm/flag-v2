"""
Logging module for the FLAG CTF Framework.
"""
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from rich.logging import RichHandler
from typing import Optional, Union

def setup_logger(name: str, log_dir: Optional[Union[str, Path]] = None, level: str = 'INFO') -> logging.Logger:
    """
    Configure and return a logger with both file and rich console handlers.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level.upper())
    
    # Avoid duplicate handlers if already configured
    if logger.hasHandlers():
        logger.handlers.clear()

    # Rich Console Handler
    console_handler = RichHandler(
        rich_tracebacks=True,
        markup=True,
        show_time=True,
        show_path=False
    )
    console_handler.setLevel(level.upper())
    console_format = logging.Formatter('%(message)s')
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # File Handler
    if log_dir is None:
        log_dir = Path('logs')
    else:
        log_dir = Path(log_dir)

    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / 'ctf.log'

    file_handler = RotatingFileHandler(
        log_file, maxBytes=5*1024*1024, backupCount=5, encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)  # File logs debug and up, regardless of console
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)

    # Prevent logger from propagating to root logger to avoid double printing
    logger.propagate = False

    return logger

def get_logger(name: str) -> logging.Logger:
    """
    Retrieves an existing logger or creates a default one.
    """
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        return setup_logger(name)
    return logger
