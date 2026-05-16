"""
File system utility functions.

This module provides utilities for working with files and directories,
including file type detection, path filtering, and safe file reading.
"""

import os
import mimetypes
from pathlib import Path
from typing import Optional, Iterator, List


# Common binary file extensions to skip
BINARY_EXTENSIONS = {
    '.pyc', '.pyo', '.so', '.dll', '.dylib', '.exe', '.bin',
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.svg',
    '.mp3', '.mp4', '.avi', '.mov', '.wav', '.flac',
    '.zip', '.tar', '.gz', '.bz2', '.7z', '.rar',
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.db', '.sqlite', '.sqlite3'
}

# Language mapping by file extension
LANGUAGE_MAP = {
    '.py': 'python',
    '.js': 'javascript',
    '.jsx': 'javascript',
    '.ts': 'typescript',
    '.tsx': 'typescript',
    '.java': 'java',
    '.c': 'c',
    '.cpp': 'cpp',
    '.cc': 'cpp',
    '.cxx': 'cpp',
    '.h': 'c',
    '.hpp': 'cpp',
    '.cs': 'csharp',
    '.go': 'go',
    '.rs': 'rust',
    '.rb': 'ruby',
    '.php': 'php',
    '.swift': 'swift',
    '.kt': 'kotlin',
    '.scala': 'scala',
    '.r': 'r',
    '.m': 'objective-c',
    '.sh': 'shell',
    '.bash': 'shell',
    '.zsh': 'shell',
    '.fish': 'shell',
    '.ps1': 'powershell',
    '.sql': 'sql',
    '.html': 'html',
    '.htm': 'html',
    '.css': 'css',
    '.scss': 'scss',
    '.sass': 'sass',
    '.less': 'less',
    '.xml': 'xml',
    '.json': 'json',
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.toml': 'toml',
    '.md': 'markdown',
    '.rst': 'restructuredtext',
    '.tex': 'latex'
}

# Common directories and patterns to ignore
DEFAULT_IGNORE_PATTERNS = [
    'node_modules',
    '__pycache__',
    '.git',
    '.svn',
    '.hg',
    '.bzr',
    'venv',
    'env',
    '.venv',
    '.env',
    'virtualenv',
    'dist',
    'build',
    'target',
    '.idea',
    '.vscode',
    '.vs',
    'coverage',
    '.coverage',
    '.pytest_cache',
    '.mypy_cache',
    '.tox',
    'eggs',
    '*.egg-info',
    '.eggs',
    'lib',
    'lib64',
    'parts',
    'sdist',
    'var',
    'wheels',
    '*.pyc',
    '*.pyo',
    '*.so',
    '.DS_Store',
    'Thumbs.db'
]


def is_text_file(file_path: str) -> bool:
    """
    Check if a file is a text file (not binary).
    
    Args:
        file_path: Path to the file to check
        
    Returns:
        True if the file is text, False if binary or cannot be determined
        
    Example:
        >>> is_text_file("script.py")
        True
        >>> is_text_file("image.png")
        False
    """
    # Check extension first
    ext = Path(file_path).suffix.lower()
    if ext in BINARY_EXTENSIONS:
        return False
    
    # Use mimetypes to check
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type:
        if mime_type.startswith('text/'):
            return True
        if mime_type in ['application/json', 'application/xml', 'application/javascript']:
            return True
        if not mime_type.startswith('text/') and '/' in mime_type:
            return False
    
    # Try to read the first chunk of the file
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(8192)
            if not chunk:
                return True  # Empty file is considered text
            
            # Check for null bytes (common in binary files)
            if b'\x00' in chunk:
                return False
            
            # Try to decode as UTF-8
            try:
                chunk.decode('utf-8')
                return True
            except UnicodeDecodeError:
                return False
                
    except (IOError, OSError):
        return False


def get_file_language(file_path: str) -> Optional[str]:
    """
    Determine the programming language of a file based on its extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Language name as string, or None if unknown
        
    Example:
        >>> get_file_language("script.py")
        'python'
        >>> get_file_language("app.js")
        'javascript'
    """
    ext = Path(file_path).suffix.lower()
    return LANGUAGE_MAP.get(ext)


def should_ignore_path(path: str, ignore_patterns: Optional[List[str]] = None) -> bool:
    """
    Check if a path should be ignored based on common patterns.
    
    Args:
        path: Path to check (file or directory)
        ignore_patterns: Optional list of additional patterns to ignore
        
    Returns:
        True if the path should be ignored, False otherwise
        
    Example:
        >>> should_ignore_path("node_modules/package")
        True
        >>> should_ignore_path("src/main.py")
        False
    """
    if ignore_patterns is None:
        ignore_patterns = []
    
    all_patterns = DEFAULT_IGNORE_PATTERNS + ignore_patterns
    path_obj = Path(path)
    
    # Check each part of the path
    for part in path_obj.parts:
        for pattern in all_patterns:
            # Handle wildcard patterns
            if '*' in pattern:
                import fnmatch
                if fnmatch.fnmatch(part, pattern):
                    return True
            # Exact match
            elif part == pattern:
                return True
    
    # Check if the file name matches any pattern
    for pattern in all_patterns:
        if '*' in pattern:
            import fnmatch
            if fnmatch.fnmatch(path_obj.name, pattern):
                return True
    
    return False


def safe_read_file(file_path: str, max_size: int = 10 * 1024 * 1024) -> Optional[str]:
    """
    Safely read a file with size limit and error handling.
    
    Args:
        file_path: Path to the file to read
        max_size: Maximum file size in bytes (default: 10MB)
        
    Returns:
        File contents as string, or None if reading failed
        
    Example:
        >>> content = safe_read_file("config.json")
        >>> if content:
        ...     print("File read successfully")
    """
    try:
        # Check file size first
        file_size = os.path.getsize(file_path)
        if file_size > max_size:
            return None
        
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
            
    except FileNotFoundError:
        return None
    except UnicodeDecodeError:
        # Try with different encoding
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
        except Exception:
            return None
    except (IOError, OSError):
        return None
    except Exception:
        return None


def walk_directory(
    root: str,
    ignore_patterns: Optional[List[str]] = None,
    include_hidden: bool = False
) -> Iterator[str]:
    """
    Walk through a directory tree yielding file paths.
    
    Args:
        root: Root directory to start walking from
        ignore_patterns: Optional list of patterns to ignore
        include_hidden: Whether to include hidden files/directories (default: False)
        
    Yields:
        File paths as strings
        
    Example:
        >>> for file_path in walk_directory("src"):
        ...     print(file_path)
    """
    if ignore_patterns is None:
        ignore_patterns = []
    
    root_path = Path(root)
    
    if not root_path.exists():
        return
    
    if not root_path.is_dir():
        # If root is a file, just yield it
        if not should_ignore_path(str(root_path), ignore_patterns):
            yield str(root_path)
        return
    
    try:
        for dirpath, dirnames, filenames in os.walk(root):
            # Filter out ignored directories (modifying in place)
            dirnames[:] = [
                d for d in dirnames
                if not should_ignore_path(os.path.join(dirpath, d), ignore_patterns)
                and (include_hidden or not d.startswith('.'))
            ]
            
            # Yield files that aren't ignored
            for filename in filenames:
                if not include_hidden and filename.startswith('.'):
                    continue
                
                file_path = os.path.join(dirpath, filename)
                
                if not should_ignore_path(file_path, ignore_patterns):
                    yield file_path
                    
    except (IOError, OSError):
        # Skip directories we can't access
        pass


def get_file_size(file_path: str) -> Optional[int]:
    """
    Get the size of a file in bytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File size in bytes, or None if file doesn't exist or error occurs
        
    Example:
        >>> size = get_file_size("data.json")
        >>> if size:
        ...     print(f"File is {size} bytes")
    """
    try:
        return os.path.getsize(file_path)
    except (IOError, OSError):
        return None


def get_relative_path(file_path: str, base_path: str) -> str:
    """
    Get the relative path of a file from a base path.
    
    Args:
        file_path: Absolute or relative file path
        base_path: Base directory path
        
    Returns:
        Relative path as string
        
    Example:
        >>> get_relative_path("/project/src/main.py", "/project")
        'src/main.py'
    """
    try:
        return str(Path(file_path).relative_to(Path(base_path)))
    except ValueError:
        # If file_path is not relative to base_path, return as-is
        return file_path

# Made with Bob
