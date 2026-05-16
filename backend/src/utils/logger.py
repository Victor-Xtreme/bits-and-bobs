"""
Centralized logging configuration.

This module provides a consistent logging setup across the application
with support for console and file output, log rotation, and color coding.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from logging.handlers import RotatingFileHandler


# ANSI color codes for console output
class LogColors:
    """ANSI color codes for terminal output."""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright foreground colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'


# Level to color mapping
LEVEL_COLORS = {
    'DEBUG': LogColors.CYAN,
    'INFO': LogColors.GREEN,
    'WARNING': LogColors.YELLOW,
    'ERROR': LogColors.RED,
    'CRITICAL': LogColors.BRIGHT_RED + LogColors.BOLD
}


class ColoredFormatter(logging.Formatter):
    """
    Custom formatter that adds color to console output.
    """
    
    def __init__(self, fmt: Optional[str] = None, datefmt: Optional[str] = None, use_colors: bool = True):
        """
        Initialize the colored formatter.
        
        Args:
            fmt: Log message format string
            datefmt: Date format string
            use_colors: Whether to use colors (disable for non-terminal output)
        """
        super().__init__(fmt, datefmt)
        self.use_colors = use_colors
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record with colors.
        
        Args:
            record: The log record to format
            
        Returns:
            Formatted log message string
        """
        if self.use_colors and record.levelname in LEVEL_COLORS:
            # Color the level name
            levelname_color = LEVEL_COLORS[record.levelname]
            record.levelname = f"{levelname_color}{record.levelname}{LogColors.RESET}"
            
            # Color the message based on level
            if record.levelno >= logging.ERROR:
                record.msg = f"{LogColors.RED}{record.msg}{LogColors.RESET}"
            elif record.levelno >= logging.WARNING:
                record.msg = f"{LogColors.YELLOW}{record.msg}{LogColors.RESET}"
        
        return super().format(record)


def setup_logger(
    name: str,
    level: str = "INFO",
    log_file: Optional[str] = None,
    log_dir: str = "logs",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    use_colors: bool = True
) -> logging.Logger:
    """
    Set up and configure a logger with console and optional file output.
    
    Args:
        name: Logger name (typically __name__ of the module)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file name (without path)
        log_dir: Directory for log files (default: "logs")
        max_bytes: Maximum size of log file before rotation (default: 10MB)
        backup_count: Number of backup log files to keep (default: 5)
        use_colors: Whether to use colored output for console (default: True)
        
    Returns:
        Configured logger instance
        
    Example:
        >>> logger = setup_logger(__name__, level="DEBUG")
        >>> logger.info("Application started")
        >>> logger.error("An error occurred")
    """
    # Create logger
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Set level
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Create formatters
    console_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    file_format = '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_formatter = ColoredFormatter(
        fmt=console_format,
        datefmt=date_format,
        use_colors=use_colors and sys.stdout.isatty()
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation (if log_file is specified)
    if log_file:
        # Create log directory if it doesn't exist
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        
        # Create rotating file handler
        file_path = log_path / log_file
        file_handler = RotatingFileHandler(
            filename=str(file_path),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter(fmt=file_format, datefmt=date_format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get an existing logger or create a new one with default settings.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
        
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Using default logger")
    """
    logger = logging.getLogger(name)
    
    # If logger has no handlers, set it up with defaults
    if not logger.handlers:
        return setup_logger(name)
    
    return logger


def set_log_level(logger: logging.Logger, level: str) -> None:
    """
    Change the log level of a logger and all its handlers.
    
    Args:
        logger: Logger instance to modify
        level: New log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Example:
        >>> logger = get_logger(__name__)
        >>> set_log_level(logger, "DEBUG")
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    for handler in logger.handlers:
        handler.setLevel(log_level)


def log_exception(logger: logging.Logger, exception: Exception, message: str = "An error occurred") -> None:
    """
    Log an exception with full traceback.
    
    Args:
        logger: Logger instance
        exception: Exception to log
        message: Optional message to include
        
    Example:
        >>> try:
        ...     risky_operation()
        ... except Exception as e:
        ...     log_exception(logger, e, "Operation failed")
    """
    logger.error(f"{message}: {str(exception)}", exc_info=True)


# Create a default application logger
default_logger = setup_logger(
    name="reposense",
    level="INFO",
    log_file="reposense.log"
)


def get_default_logger() -> logging.Logger:
    """
    Get the default application logger.
    
    Returns:
        Default logger instance
        
    Example:
        >>> logger = get_default_logger()
        >>> logger.info("Using default logger")
    """
    return default_logger
    
    # Set formatter
    file_format = '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    file_formatter = logging.Formatter(fmt=file_format, datefmt=date_format)
    file_handler.setFormatter(file_formatter)
    
    # Add handler to logger
    logger.addHandler(file_handler)


# Create a default application logger
app_logger = setup_logger(
    name="reposense",
    level="INFO",
    log_file="reposense.log",
    use_colors=True
)

# Made with Bob
