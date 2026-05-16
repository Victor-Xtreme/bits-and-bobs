"""
Utility modules for the RepoSense codebase analysis tool.

This package provides various utility functions for:
- AST parsing (ast_parser.py)
- File operations (file_utils.py)
- Logging (logger.py)
"""

# Import main functions from ast_parser
from .ast_parser import parse_python_file

# Import main functions from file_utils
from .file_utils import (
    is_text_file,
    get_file_language,
    should_ignore_path,
    safe_read_file,
    walk_directory,
    get_file_size,
    get_relative_path
)

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
    # AST parser
    'parse_python_file',
    
    # File utilities
    'is_text_file',
    'get_file_language',
    'should_ignore_path',
    'safe_read_file',
    'walk_directory',
    'get_file_size',
    'get_relative_path',
    
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
