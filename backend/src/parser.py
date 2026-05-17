"""
RepoSense Codebase Parser
Parses codebases into structured ParsedCodebase models
"""

import os
import asyncio
import logging
from pathlib import Path
from typing import Optional, List, Dict, Tuple

from .models import (
    ParsedCodebase,
    ParsedFile,
    ParsedClass,
    ParsedFunction,
    StepStatus
)
from .config import settings
from .jobs import update_job_progress

logger = logging.getLogger(__name__)


def _collect_all_files(path: Path) -> List[Path]:
    """Collect all files from directory, skipping common ignore directories."""
    all_files = []
    for root, dirs, files in os.walk(path):
        # Skip common directories to ignore
        dirs[:] = [d for d in dirs if d not in {
            'node_modules', '.git', '__pycache__', 'venv', 'env',
            '.venv', 'dist', 'build', 'target', '.next', '.nuxt'
        }]
        
        for file in files:
            file_path = Path(root) / file
            all_files.append(file_path)
    
    return all_files


def _filter_files_by_language_and_size(
    all_files: List[Path],
    supported_languages: List[str],
    max_size: int
) -> List[Path]:
    """Filter files by supported language extensions and size limits."""
    filtered_files = []
    
    for file_path in all_files:
        # Check file extension
        ext = file_path.suffix.lstrip('.')
        if ext not in supported_languages:
            continue
        
        # Check file size
        try:
            if file_path.stat().st_size > max_size:
                continue
        except OSError:
            continue
        
        filtered_files.append(file_path)
    
    return filtered_files


def _validate_filtered_files(
    filtered_files: List[Path],
    all_files: List[Path],
    supported_languages: List[str]
) -> None:
    """Validate that we have files to parse after filtering."""
    if not filtered_files:
        if all_files:
            # Files were found but all filtered out
            raise ValueError(
                f"No supported files found in codebase. "
                f"All {len(all_files)} files were filtered out (likely due to size limits or unsupported extensions). "
                f"Max file size: {settings.max_file_size_mb}MB, "
                f"Supported languages: {', '.join(supported_languages)}"
            )
        else:
            raise ValueError("No files found in codebase directory")


async def _parse_files_with_progress(
    filtered_files: List[Path],
    base_path: Path,
    job_id: Optional[str]
) -> Tuple[List[ParsedFile], Dict[str, List[str]]]:
    """Parse all files and build import graph with progress tracking."""
    parsed_files = []
    import_graph = {}
    total_files = len(filtered_files)
    
    for idx, file_path in enumerate(filtered_files):
        # Update progress if job_id provided
        if job_id:
            update_job_progress(
                job_id,
                step_index=0,
                status=StepStatus.active,
                files_processed=idx,
                files_total=total_files,
                current_file=str(file_path.relative_to(base_path))
            )
        
        # Parse the file
        parsed_file = await parse_file(file_path, base_path)
        parsed_files.append(parsed_file)
        
        # Build import graph
        if parsed_file.imports:
            import_graph[parsed_file.path] = parsed_file.imports
    
    # Final progress update
    if job_id:
        update_job_progress(
            job_id,
            step_index=0,
            status=StepStatus.active,
            files_processed=total_files,
            files_total=total_files
        )
    
    return parsed_files, import_graph


async def parse_codebase(local_path: str, job_id: Optional[str] = None) -> ParsedCodebase:
    """
    Parse a codebase directory into a structured ParsedCodebase model.
    
    Args:
        local_path: Path to the codebase directory
        job_id: Optional job ID for progress tracking
        
    Returns:
        ParsedCodebase with all files, classes, functions, and import graph
        
    Raises:
        FileNotFoundError: If local_path doesn't exist
        ValueError: If no supported files found
    """
    path = Path(local_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Path does not exist: {local_path}")
    
    if not path.is_dir():
        raise ValueError(f"Path is not a directory: {local_path}")
    
    # Get supported languages and limits
    _lang_to_ext = {
        'python': 'py', 'javascript': 'js', 'typescript': 'ts',
        'java': 'java', 'go': 'go', 'rust': 'rs',
    }
    supported_languages = [
        _lang_to_ext.get(lang, lang)
        for lang in settings.get_supported_languages_list()
    ]
    max_size = settings.get_max_file_size_bytes()
    
    # Collect and filter files
    all_files = _collect_all_files(path)
    filtered_files = _filter_files_by_language_and_size(all_files, supported_languages, max_size)
    _validate_filtered_files(filtered_files, all_files, supported_languages)
    
    # Apply max files limit
    original_count = len(filtered_files)
    if original_count > settings.max_files_per_analysis:
        logger.warning(
            f"Codebase has {original_count} files, limiting to {settings.max_files_per_analysis}"
        )
        filtered_files = filtered_files[:settings.max_files_per_analysis]
    
    # Parse files and build import graph
    parsed_files, import_graph = await _parse_files_with_progress(filtered_files, path, job_id)
    
    return ParsedCodebase(
        files=parsed_files,
        import_graph=import_graph
    )


async def parse_file(file_path: Path, base_path: Path) -> ParsedFile:
    """
    Parse a single file into a ParsedFile model.
    
    Args:
        file_path: Path to the file
        base_path: Base path of the codebase (for relative paths)
        
    Returns:
        ParsedFile with classes, functions, and imports
    """
    # Get relative path
    try:
        rel_path = str(file_path.relative_to(base_path))
    except ValueError:
        rel_path = str(file_path)
    
    # Determine language from extension
    ext = file_path.suffix.lstrip('.')
    language = ext
    
    # Read file content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError as e:
        logger.warning(f"Failed to decode file {rel_path}: {str(e)}")
        return ParsedFile(
            path=rel_path,
            language=language,
            imports=[],
            classes=[],
            functions=[]
        )
    except Exception as e:
        logger.error(f"Failed to read file {rel_path}: {str(e)}")
        return ParsedFile(
            path=rel_path,
            language=language,
            imports=[],
            classes=[],
            functions=[]
        )
    
    # Parse based on language
    if language in ['python', 'py']:
        return await parse_python_file(rel_path, content)
    elif language in ['javascript', 'typescript', 'js', 'ts']:
        return await parse_javascript_file(rel_path, content, language)
    else:
        # For unsupported languages, return basic structure
        return ParsedFile(
            path=rel_path,
            language=language,
            imports=[],
            classes=[],
            functions=[]
        )


async def parse_python_file(rel_path: str, content: str) -> ParsedFile:
    """
    Parse a Python file using AST.
    
    Args:
        rel_path: Relative path to the file
        content: File content
        
    Returns:
        ParsedFile with parsed Python structures
    """
    import ast
    
    classes = []
    functions = []
    imports = []
    
    try:
        tree = ast.parse(content)
        
        # Extract imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        
        # Extract top-level classes and functions
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                parsed_class = parse_python_class(node, rel_path, None)
                classes.append(parsed_class)
                
                # Extract methods
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) or isinstance(item, ast.AsyncFunctionDef):
                        method = parse_python_function(item, rel_path, parsed_class.id)
                        functions.append(method)
            
            elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                func = parse_python_function(node, rel_path, None)
                functions.append(func)
    
    except SyntaxError as e:
        logger.warning(f"Syntax error in {rel_path}, skipping: {e}")
    
    return ParsedFile(
        path=rel_path,
        language='python',
        imports=list(set(imports)),  # Remove duplicates
        classes=classes,
        functions=functions
    )


def parse_python_class(node, rel_path: str, parent_id: Optional[str]) -> ParsedClass:
    """Parse a Python class node"""
    import ast
    
    class_id = f"{rel_path}::{node.name}"
    if parent_id:
        class_id = f"{parent_id}::{node.name}"
    
    docstring = ast.get_docstring(node)
    bases = [base.id if isinstance(base, ast.Name) else str(base) for base in node.bases]
    
    return ParsedClass(
        id=class_id,
        name=node.name,
        parent_id=parent_id,
        line_start=node.lineno,
        line_end=node.end_lineno or node.lineno,
        docstring=docstring,
        bases=bases
    )


def parse_python_function(node, rel_path: str, parent_id: Optional[str]) -> ParsedFunction:
    """Parse a Python function node"""
    import ast
    
    func_id = f"{rel_path}::{node.name}"
    if parent_id:
        func_id = f"{parent_id}::{node.name}"
    
    docstring = ast.get_docstring(node)
    params = [arg.arg for arg in node.args.args]
    
    # Extract return type if available
    returns = None
    if node.returns:
        if isinstance(node.returns, ast.Name):
            returns = node.returns.id
        else:
            returns = ast.unparse(node.returns) if hasattr(ast, 'unparse') else None
    
    return ParsedFunction(
        id=func_id,
        name=node.name,
        parent_id=parent_id,
        line_start=node.lineno,
        line_end=node.end_lineno or node.lineno,
        docstring=docstring,
        params=params,
        returns=returns
    )


async def parse_javascript_file(rel_path: str, content: str, language: str) -> ParsedFile:
    """
    Parse a JavaScript/TypeScript file.
    
    Note: This is a simplified parser. For production, use a proper JS/TS parser.
    
    Args:
        rel_path: Relative path to the file
        content: File content
        language: 'javascript' or 'typescript'
        
    Returns:
        ParsedFile with basic JS/TS structures
    """
    import re
    
    imports = []
    classes = []
    functions = []
    
    # Extract imports (simplified)
    import_patterns = [
        r'import\s+.*?\s+from\s+[\'"](.+?)[\'"]',
        r'require\([\'"](.+?)[\'"]\)',
    ]
    
    for pattern in import_patterns:
        matches = re.finditer(pattern, content)
        for match in matches:
            imports.append(match.group(1))
    
    # Extract classes (simplified)
    class_pattern = r'class\s+(\w+)'
    for match in re.finditer(class_pattern, content):
        class_name = match.group(1)
        line_num = content[:match.start()].count('\n') + 1
        
        classes.append(ParsedClass(
            id=f"{rel_path}::{class_name}",
            name=class_name,
            parent_id=None,
            line_start=line_num,
            line_end=line_num,
            docstring=None,
            bases=[]
        ))
    
    # Extract functions (simplified)
    func_patterns = [
        r'(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(',
        r'const\s+(\w+)\s*=\s*(?:async\s+)?\(',
    ]
    
    for pattern in func_patterns:
        for match in re.finditer(pattern, content):
            func_name = match.group(1)
            line_num = content[:match.start()].count('\n') + 1
            
            functions.append(ParsedFunction(
                id=f"{rel_path}::{func_name}",
                name=func_name,
                parent_id=None,
                line_start=line_num,
                line_end=line_num,
                docstring=None,
                params=[],
                returns=None
            ))
    
    return ParsedFile(
        path=rel_path,
        language=language,
        imports=list(set(imports)),
        classes=classes,
        functions=functions
    )

# Made with Bob
