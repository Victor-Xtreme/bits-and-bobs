"""
Python AST (Abstract Syntax Tree) parsing utilities.

This module provides functions to parse Python source files and extract
structural information such as imports, classes, and functions.
"""

import ast
from typing import Dict, List, Optional, Any


def parse_python_file(file_path: str) -> Dict[str, Any]:
    """
    Parse a Python file and extract its structure.
    
    Args:
        file_path: Path to the Python file to parse
        
    Returns:
        Dictionary containing:
            - imports: List of import statements
            - classes: List of class definitions with details
            - functions: List of function definitions with details
            - parse_error: Error message if parsing failed (optional)
            
    Example:
        >>> result = parse_python_file("example.py")
        >>> print(result['classes'])
        [{'name': 'MyClass', 'line_start': 10, ...}]
    """
    result: Dict[str, Any] = {
        'imports': [],
        'classes': [],
        'functions': []
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # Parse the source code into an AST
        tree = ast.parse(source_code, filename=file_path)
        
        # Extract imports
        result['imports'] = _extract_imports(tree)
        
        # Extract top-level classes and functions
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                result['classes'].append(_extract_class_info(node))
            elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                result['functions'].append(_extract_function_info(node))
                
    except SyntaxError as e:
        result['parse_error'] = f"Syntax error at line {e.lineno}: {e.msg}"
    except FileNotFoundError:
        result['parse_error'] = f"File not found: {file_path}"
    except UnicodeDecodeError:
        result['parse_error'] = "Unable to decode file (not valid UTF-8)"
    except Exception as e:
        result['parse_error'] = f"Unexpected error: {str(e)}"
    
    return result


def _extract_imports(tree: ast.AST) -> List[str]:
    """
    Extract all import statements from an AST.
    
    Args:
        tree: The AST to extract imports from
        
    Returns:
        List of import statement strings
    """
    imports = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.asname:
                    imports.append(f"import {alias.name} as {alias.asname}")
                else:
                    imports.append(f"import {alias.name}")
                    
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            level = "." * node.level
            
            for alias in node.names:
                if alias.asname:
                    imports.append(f"from {level}{module} import {alias.name} as {alias.asname}")
                else:
                    imports.append(f"from {level}{module} import {alias.name}")
    
    return imports


def _extract_class_info(node: ast.ClassDef) -> Dict[str, Any]:
    """
    Extract information from a class definition node.
    
    Args:
        node: The ClassDef AST node
        
    Returns:
        Dictionary with class information
    """
    class_info = {
        'name': node.name,
        'line_start': node.lineno,
        'line_end': node.end_lineno or node.lineno,
        'docstring': ast.get_docstring(node),
        'bases': [],
        'methods': []
    }
    
    # Extract base classes
    for base in node.bases:
        if isinstance(base, ast.Name):
            class_info['bases'].append(base.id)
        elif isinstance(base, ast.Attribute):
            class_info['bases'].append(_get_attribute_name(base))
    
    # Extract methods
    for item in node.body:
        if isinstance(item, ast.FunctionDef) or isinstance(item, ast.AsyncFunctionDef):
            method_info = _extract_function_info(item)
            method_info['is_method'] = True
            class_info['methods'].append(method_info)
    
    return class_info


def _extract_function_info(node: ast.FunctionDef | ast.AsyncFunctionDef) -> Dict[str, Any]:
    """
    Extract information from a function definition node.
    
    Args:
        node: The FunctionDef or AsyncFunctionDef AST node
        
    Returns:
        Dictionary with function information
    """
    function_info = {
        'name': node.name,
        'line_start': node.lineno,
        'line_end': node.end_lineno or node.lineno,
        'docstring': ast.get_docstring(node),
        'params': [],
        'returns': None,
        'is_async': isinstance(node, ast.AsyncFunctionDef)
    }
    
    # Extract parameters
    args = node.args
    
    # Regular arguments
    for arg in args.args:
        param = {'name': arg.arg, 'annotation': None}
        if arg.annotation:
            param['annotation'] = _get_annotation_string(arg.annotation)
        function_info['params'].append(param)
    
    # *args
    if args.vararg:
        param = {'name': f"*{args.vararg.arg}", 'annotation': None}
        if args.vararg.annotation:
            param['annotation'] = _get_annotation_string(args.vararg.annotation)
        function_info['params'].append(param)
    
    # **kwargs
    if args.kwarg:
        param = {'name': f"**{args.kwarg.arg}", 'annotation': None}
        if args.kwarg.annotation:
            param['annotation'] = _get_annotation_string(args.kwarg.annotation)
        function_info['params'].append(param)
    
    # Extract return type annotation
    if node.returns:
        function_info['returns'] = _get_annotation_string(node.returns)
    
    return function_info


def _get_annotation_string(annotation: ast.AST) -> str:
    """
    Convert an annotation AST node to a string representation.
    
    Args:
        annotation: The annotation AST node
        
    Returns:
        String representation of the annotation
    """
    try:
        return ast.unparse(annotation)
    except Exception:
        # Fallback for complex annotations
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Constant):
            return str(annotation.value)
        elif isinstance(annotation, ast.Attribute):
            return _get_attribute_name(annotation)
        else:
            return "Unknown"


def _get_attribute_name(node: ast.Attribute) -> str:
    """
    Get the full name of an attribute node (e.g., 'module.Class').
    
    Args:
        node: The Attribute AST node
        
    Returns:
        Full attribute name as string
    """
    parts = [node.attr]
    current = node.value
    
    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value
    
    if isinstance(current, ast.Name):
        parts.append(current.id)
    
    return ".".join(reversed(parts))

# Made with Bob
