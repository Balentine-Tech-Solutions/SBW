"""
Logging Configuration Module
SBWv1.i2 Mark I Prototype

Sets up consistent logging across the SBW CLI tool.
Supports console and file logging with configurable levels.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

try:
    import colorama
    from colorama import Fore, Back, Style
    colorama.init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support for console output."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if COLORAMA_AVAILABLE:
            self.colors = {
                logging.DEBUG: Fore.CYAN,
                logging.INFO: Fore.GREEN,
                logging.WARNING: Fore.YELLOW,
                logging.ERROR: Fore.RED,
                logging.CRITICAL: Fore.RED + Back.WHITE
            }
        else:
            self.colors = {}
    
    def format(self, record):
        # Format the message normally
        formatted = super().format(record)
        
        # Add color if available
        if COLORAMA_AVAILABLE and record.levelno in self.colors:
            color = self.colors[record.levelno]
            formatted = f"{color}{formatted}{Style.RESET_ALL}"
            
        return formatted


def setup_logging(
    level: int = logging.INFO,
    format_string: Optional[str] = None,
    enable_file_logging: bool = False,
    log_file: Optional[Path] = None,
    console_colors: bool = True
) -> logging.Logger:
    """
    Set up logging configuration for the SBW CLI tool.
    
    Args:
        level: Logging level (logging.DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom format string for log messages
        enable_file_logging: Whether to enable file logging
        log_file: Path to log file (if file logging enabled)
        console_colors: Whether to use colored console output
        
    Returns:
        Root logger instance
    """
    # Default format string
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Clear any existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    root_logger.setLevel(level)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    if console_colors and COLORAMA_AVAILABLE:
        console_formatter = ColoredFormatter(format_string)
    else:
        console_formatter = logging.Formatter(format_string)
        
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if requested)
    if enable_file_logging:
        if log_file is None:
            log_file = Path('sbw_cli.log')
            
        # Ensure log directory exists
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        file_handler.setLevel(level)
        
        # File formatter (no colors)
        file_formatter = logging.Formatter(format_string)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
        
        root_logger.info(f"File logging enabled: {log_file}")
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def log_system_info() -> None:
    """Log system and environment information for debugging."""
    logger = get_logger(__name__)
    
    import platform
    import sys
    
    logger.info("=== SBW CLI System Information ===")
    logger.info(f"Platform: {platform.platform()}")
    logger.info(f"Python: {sys.version}")
    logger.info(f"Architecture: {platform.architecture()}")
    logger.info(f"Processor: {platform.processor()}")
    
    # Check for required libraries
    libraries = {
        'cryptography': 'Cryptographic operations',
        'lz4': 'LZ4 compression',
        'numpy': 'Numerical operations', 
        'pandas': 'Data analysis',
        'matplotlib': 'Plotting and visualization',
        'colorama': 'Colored console output'
    }
    
    logger.info("=== Library Availability ===")
    for lib_name, description in libraries.items():
        try:
            __import__(lib_name)
            logger.info(f"✓ {lib_name}: Available ({description})")
        except ImportError:
            logger.warning(f"✗ {lib_name}: Not available ({description})")
    
    logger.info("=== Environment Ready ===")