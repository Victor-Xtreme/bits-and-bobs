"""
Utility modules for the RepoSense codebase analysis tool.

This package provides various utility functions for:
- Logging (logger.py)
"""

# Import main functions from logger
from .logger import (
    setup_logger,
    get_logger,
    set_log_level,
    log_exception,
    get_default_logger
)

# Define what's available when using "from utils import *"
__all__ = [
    # Logger utilities
    'setup_logger',
    'get_logger',
    'set_log_level',
    'log_exception',
    'get_default_logger'
]

# Package metadata
__version__ = '1.0.0'
__author__ = 'RepoSense Team'

# Made with Bob
