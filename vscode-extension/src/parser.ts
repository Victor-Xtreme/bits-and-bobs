
/**
 * Local codebase parser for the RepoSense VS Code extension.
 * Mirrors the logic of backend/src/parser.py so parsing runs
 * on the developer's machine instead of the server.
 *
 * Supported languages: Python, JavaScript, TypeScript
 * Other language files are collected but returned with empty
 * classes/functions/imports (same behaviour as the backend).
 */

import * as fs from 'node:fs';
import * as path from 'node:path';

// ---------------------------------------------------------------------------
// Types — must exactly match the Pydantic models in backend/src/models.py
// ---------------------------------------------------------------------------

export interface ParsedClass {
    id: string;
    name: string;
    parent_id: string | null;
    line_start: number;
    line_end: number;
    docstring: string | null;
    bases: string[];
}

export interface ParsedFunction {
    id: string;
    name: string;
    parent_id: string | null;
    line_start: number;
    line_end: number;
    docstring: string | null;
    params: string[];
    returns: string | null;
}

export interface ParsedFile {
    path: string;
    language: string;
    imports: string[];
    classes: ParsedClass[];
    functions: ParsedFunction[];
}

export interface ParsedCodebase {
    files: ParsedFile[];
    import_graph: Record<string, string[]>;
}

// ---------------------------------------------------------------------------
// Constants — match backend/src/config.py defaults
// ---------------------------------------------------------------------------

/** Directories to skip when walking the workspace. */
const SKIP_DIRS = new Set([
    'node_modules', '.git', '__pycache__', 'venv', 'env',
    '.venv', 'dist', 'build', 'target', '.next', '.nuxt', 'out',
]);

/** File extensions the backend supports. */
const SUPPORTED_EXTENSIONS = new Set(['py', 'js', 'ts', 'java', 'go', 'rs', 'c', 'cpp', 'h', 'hpp']);

/** Backend default: 1 MB per file. */
const MAX_FILE_BYTES = 1 * 1024 * 1024;

/** Backend default: 500 files per analysis. */
const MAX_FILES = 500;

// ---------------------------------------------------------------------------
// File collection
// ---------------------------------------------------------------------------

/**
 * Recursively collect all file paths under rootPath,
 * skipping directories listed in SKIP_DIRS.
 */
function collectAllFiles(rootPath: string): string[] {
    const results: string[] = [];

    function walk(dir: string): void {
        let entries: fs.Dirent[];
        try {
            entries = fs.readdirSync(dir, { withFileTypes: true });
        } catch {
            return; // unreadable directory — skip silently
        }

        for (const entry of entries) {
            if (entry.isDirectory()) {
                if (!SKIP_DIRS.has(entry.name)) {
                    walk(path.join(dir, entry.name));
                }
            } else if (entry.isFile()) {
                results.push(path.join(dir, entry.name));
            }
        }
    }

    walk(rootPath);
    return results;
}

/**
 * Keep only files whose extension is in SUPPORTED_EXTENSIONS
 * and whose size is within MAX_FILE_BYTES.
 */
function filterFiles(files: string[]): string[] {
    return files.filter(f => {
        const ext = path.extname(f).replace('.', '').toLowerCase();
        if (!SUPPORTED_EXTENSIONS.has(ext)) {
            return false;
        }
        try {
            return fs.statSync(f).size <= MAX_FILE_BYTES;
        } catch {
            return false;
        }
    });
}

// ---------------------------------------------------------------------------
// Line-number helper
// ---------------------------------------------------------------------------

/** Return the 1-based line number of the character at index in content. */
function lineAt(content: string, index: number): number {
    return content.slice(0, index).split('\n').length;
}

// ---------------------------------------------------------------------------
// Python parser
// ---------------------------------------------------------------------------

/**
 * Parse a Python file using regular expressions.
 * (We cannot use Python's ast module in Node, so we use regex —
 * the same approach the backend uses for JS/TS files.)
 */
function parsePythonFile(relPath: string, content: string): ParsedFile {
    const imports: string[] = [];
    const classes: ParsedClass[] = [];
    const functions: ParsedFunction[] = [];

    // --- Imports ---
    // Matches: import foo.bar  or  from foo.bar import ...
    const importRe = /^(?:import ([\w.]+)|from ([\w.]+) import)/gm;
    let m: RegExpExecArray | null;
    while ((m = importRe.exec(content)) !== null) {
        const name = m[1] ?? m[2];
        if (name) {
            imports.push(name);
        }
    }

    // --- Classes ---
    // Matches: class Foo:  or  class Foo(Bar, Baz):
    const classRe = /^class\s+(\w+)\s*(?:\(([^)]*)\))?s*:/gm;
    while ((m = classRe.exec(content)) !== null) {
        const name = m[1];
        const rawBases = m[2] ?? '';
        const bases = rawBases
            .split(',')
            .map(b => b.trim())
            .filter(Boolean);
        classes.push({
            id: `${relPath}::${name}`,
            name,
            parent_id: null,
            line_start: lineAt(content, m.index),
            line_end: lineAt(content, m.index),
            docstring: null,
            bases,
        });
    }

    // --- Functions (top-level and methods) ---
    // Matches: def foo(a, b):  or  async def foo(a: int) -> str:
    const funcRe = /^(?:    )?(?:async\s+)?def\s+(\w+)\s*\(([^)]*)\)/gm;
    while ((m = funcRe.exec(content)) !== null) {
        const name = m[1];
        const rawParams = m[2] ?? '';
        const params = rawParams
            .split(',')
            .map(p => p.trim().split(':')[0].trim().split('=')[0].trim())
            .filter(p => p && p !== 'self' && p !== 'cls');
        functions.push({
            id: `${relPath}::${name}`,
            name,
            parent_id: null,
            line_start: lineAt(content, m.index),
            line_end: lineAt(content, m.index),
            docstring: null,
            params,
            returns: null,
        });
    }

    return {
        path: relPath,
        language: 'python',
        imports: [...new Set(imports)],
        classes,
        functions,
    };
}

// ---------------------------------------------------------------------------
// JavaScript / TypeScript parser
// ---------------------------------------------------------------------------

/**
 * Parse a JS or TS file.
 * Uses the same regex patterns as the Python backend's parse_javascript_file.
 */
function parseJsTsFile(
    relPath: string,
    content: string,
    language: 'javascript' | 'typescript'
): ParsedFile {
    const imports: string[] = [];
    const classes: ParsedClass[] = [];
    const functions: ParsedFunction[] = [];
    let m: RegExpExecArray | null;

    // --- Imports ---
    const importPatterns: RegExp[] = [
        /import\s+.*?\s+from\s+['"](.+?)['"]/g,
        /require\(['"](.+?)['"]\)/g,
    ];
    for (const pattern of importPatterns) {
        while ((m = pattern.exec(content)) !== null) {
            imports.push(m[1]);
        }
    }

    // --- Classes ---
    const classRe = /class\s+(\w+)/g;
    while ((m = classRe.exec(content)) !== null) {
        const name = m[1];
        classes.push({
            id: `${relPath}::${name}`,
            name,
            parent_id: null,
            line_start: lineAt(content, m.index),
            line_end: lineAt(content, m.index),
            docstring: null,
            bases: [],
        });
    }

    // --- Functions ---
    const funcPatterns: RegExp[] = [
        /(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(/g,
        /const\s+(\w+)\s*=\s*(?:async\s+)?\(/g,
    ];
    for (const pattern of funcPatterns) {
        while ((m = pattern.exec(content)) !== null) {
            const name = m[1];
            functions.push({
                id: `${relPath}::${name}`,
                name,
                parent_id: null,
                line_start: lineAt(content, m.index),
                line_end: lineAt(content, m.index),
                docstring: null,
                params: [],
                returns: null,
            });
        }
    }

    return {
        path: relPath,
        language,
        imports: [...new Set(imports)],
        classes,
        functions,
    };
}

// ---------------------------------------------------------------------------
// C / C++ parser
// ---------------------------------------------------------------------------

/**
 * Parse a C or C++ file using regular expressions.
 *
 * Extracts:
 * - #include directives as imports
 * - struct/class definitions as classes
 * - Function definitions as functions
 *
 * Header files (.h / .hpp) are parsed with the same logic — they commonly
 * contain class definitions and function declarations worth surfacing.
 */
async function parseCFile(
    relPath: string,
    content: string,
    language: string
): Promise<ParsedFile> {
    const imports: string[] = [];
    const classes: ParsedClass[] = [];
    const functions: ParsedFunction[] = [];
    let m: RegExpExecArray | null;

    // --- Includes ---
    // Matches: #include <stdio.h>  or  #include "myfile.h"
    const includeRe = /#include\s+[<"]([^>"]+)[>"]/g;
    while ((m = includeRe.exec(content)) !== null) {
        imports.push(m[1]);
    }

    // --- Classes and structs ---
    // Requires an opening brace so forward declarations ("struct Foo;") are
    // ignored.
    const classRe = /(?:class|struct)\s+(\w+)\s*(?::[^{]*)?\{/g;
    while ((m = classRe.exec(content)) !== null) {
        const name = m[1];
        classes.push({
            id: `${relPath}::${name}`,
            name,
            parent_id: null,
            line_start: lineAt(content, m.index),
            line_end: lineAt(content, m.index),
            docstring: null,
            bases: [],
        });
    }

    // --- Function definitions ---
    // Matches a return type followed by a name, parentheses, and an opening
    // brace. Control-flow keywords are explicitly excluded.
    const skipNames = new Set(['if', 'for', 'while', 'switch', 'else', 'do']);
    const funcRe = /(?:^|\n)\s*(?!if|for|while|switch|else|do\b)(?:[\w:*&<>]+\s+)+(\w+)\s*\([^;)]*\)\s*(?:const\s*)?\{/g;
    while ((m = funcRe.exec(content)) !== null) {
        const name = m[1];
        if (skipNames.has(name)) {
            continue;
        }
        functions.push({
            id: `${relPath}::${name}`,
            name,
            parent_id: null,
            line_start: lineAt(content, m.index),
            line_end: lineAt(content, m.index),
            docstring: null,
            params: [],
            returns: null,
        });
    }

    return {
        path: relPath,
        language,
        imports: [...new Set(imports)],
        classes,
        functions,
    };
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Parse an entire workspace directory into a ParsedCodebase.
 *
 * @param workspacePath  Absolute path to the workspace root.
 * @param onProgress     Optional callback called once per file.
 *                       done  = number of files processed so far
 *                       total = total files to process
 *                       file  = relative path of the file just processed
 *                       Pass an empty string for file on the final call.
 * @returns Fully populated ParsedCodebase ready to POST to /analyze-parsed.
 * @throws  Error if no supported source files are found.
 */
export async function parseWorkspace(
    workspacePath: string,
    onProgress?: (done: number, total: number, file: string) => void
): Promise<ParsedCodebase> {
    // Collect and filter
    const allFiles = collectAllFiles(workspacePath);
    let filtered = filterFiles(allFiles);

    if (filtered.length === 0) {
        throw new Error(
            'No supported source files found in workspace. ' +
            `Supported extensions: ${[...SUPPORTED_EXTENSIONS].join(', ')}`
        );
    }

    if (filtered.length > MAX_FILES) {
        filtered = filtered.slice(0, MAX_FILES);
    }

    const parsedFiles: ParsedFile[] = [];
    const importGraph: Record<string, string[]> = {};

    for (let i = 0; i < filtered.length; i++) {
        const absPath = filtered[i];
        // Normalise path separators to forward slashes (Windows-safe)
        const relPath = path
            .relative(workspacePath, absPath)
            .replace(/\\/g, '/');
        const ext = path.extname(absPath).replace('.', '').toLowerCase();

        onProgress?.(i, filtered.length, relPath);

        // Read file content
        let content: string;
        try {
            content = fs.readFileSync(absPath, 'utf8');
        } catch {
            // Unreadable file — include a skeleton entry, same as backend
            parsedFiles.push({
                path: relPath,
                language: ext,
                imports: [],
                classes: [],
                functions: [],
            });
            continue;
        }

        // Dispatch to language parser
        let parsed: ParsedFile;
        if (ext === 'py') {
            parsed = parsePythonFile(relPath, content);
        } else if (ext === 'js') {
            parsed = parseJsTsFile(relPath, content, 'javascript');
        } else if (ext === 'ts') {
            parsed = parseJsTsFile(relPath, content, 'typescript');
        } else if (ext === 'c' || ext === 'h') {
            parsed = await parseCFile(relPath, content, ext === 'h' ? 'c_header' : 'c');
        } else if (ext === 'cpp' || ext === 'hpp') {
            parsed = await parseCFile(relPath, content, ext === 'hpp' ? 'cpp_header' : 'cpp');
        } else {
            // java, go, rs — skeleton entry (no parser yet)
            parsed = {
                path: relPath,
                language: ext,
                imports: [],
                classes: [],
                functions: [],
            };
        }

        parsedFiles.push(parsed);

        // Build import graph
        if (parsed.imports.length > 0) {
            importGraph[parsed.path] = parsed.imports;
        }
    }

    // Final progress callback with empty file string
    onProgress?.(filtered.length, filtered.length, '');

    return {
        files: parsedFiles,
        import_graph: importGraph,
    };
}