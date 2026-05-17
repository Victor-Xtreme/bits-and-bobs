"use strict";
/**
 * Local codebase parser for the RepoSense VS Code extension.
 * Mirrors the logic of backend/src/parser.py so parsing runs
 * on the developer's machine instead of the server.
 *
 * Supported languages: Python, JavaScript, TypeScript
 * Other language files are collected but returned with empty
 * classes/functions/imports (same behaviour as the backend).
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.parseWorkspace = void 0;
const fs = __importStar(require("node:fs"));
const path = __importStar(require("node:path"));
// ---------------------------------------------------------------------------
// Constants — match backend/src/config.py defaults
// ---------------------------------------------------------------------------
/** Directories to skip when walking the workspace. */
const SKIP_DIRS = new Set([
    'node_modules', '.git', '__pycache__', 'venv', 'env',
    '.venv', 'dist', 'build', 'target', '.next', '.nuxt', 'out',
]);
/** File extensions the backend supports. */
const SUPPORTED_EXTENSIONS = new Set(['py', 'js', 'ts', 'java', 'go', 'rs']);
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
function collectAllFiles(rootPath) {
    const results = [];
    function walk(dir) {
        let entries;
        try {
            entries = fs.readdirSync(dir, { withFileTypes: true });
        }
        catch {
            return; // unreadable directory — skip silently
        }
        for (const entry of entries) {
            if (entry.isDirectory()) {
                if (!SKIP_DIRS.has(entry.name)) {
                    walk(path.join(dir, entry.name));
                }
            }
            else if (entry.isFile()) {
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
function filterFiles(files) {
    return files.filter(f => {
        const ext = path.extname(f).replace('.', '').toLowerCase();
        if (!SUPPORTED_EXTENSIONS.has(ext)) {
            return false;
        }
        try {
            return fs.statSync(f).size <= MAX_FILE_BYTES;
        }
        catch {
            return false;
        }
    });
}
// ---------------------------------------------------------------------------
// Line-number helper
// ---------------------------------------------------------------------------
/** Return the 1-based line number of the character at index in content. */
function lineAt(content, index) {
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
function parsePythonFile(relPath, content) {
    const imports = [];
    const classes = [];
    const functions = [];
    // --- Imports ---
    // Matches: import foo.bar  or  from foo.bar import ...
    const importRe = /^(?:import ([\w.]+)|from ([\w.]+) import)/gm;
    let m;
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
function parseJsTsFile(relPath, content, language) {
    const imports = [];
    const classes = [];
    const functions = [];
    let m;
    // --- Imports ---
    const importPatterns = [
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
    const funcPatterns = [
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
async function parseWorkspace(workspacePath, onProgress) {
    // Collect and filter
    const allFiles = collectAllFiles(workspacePath);
    let filtered = filterFiles(allFiles);
    if (filtered.length === 0) {
        throw new Error('No supported source files found in workspace. ' +
            `Supported extensions: ${[...SUPPORTED_EXTENSIONS].join(', ')}`);
    }
    if (filtered.length > MAX_FILES) {
        filtered = filtered.slice(0, MAX_FILES);
    }
    const parsedFiles = [];
    const importGraph = {};
    for (let i = 0; i < filtered.length; i++) {
        const absPath = filtered[i];
        // Normalise path separators to forward slashes (Windows-safe)
        const relPath = path
            .relative(workspacePath, absPath)
            .replace(/\\/g, '/');
        const ext = path.extname(absPath).replace('.', '').toLowerCase();
        onProgress?.(i, filtered.length, relPath);
        // Read file content
        let content;
        try {
            content = fs.readFileSync(absPath, 'utf8');
        }
        catch {
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
        let parsed;
        if (ext === 'py') {
            parsed = parsePythonFile(relPath, content);
        }
        else if (ext === 'js') {
            parsed = parseJsTsFile(relPath, content, 'javascript');
        }
        else if (ext === 'ts') {
            parsed = parseJsTsFile(relPath, content, 'typescript');
        }
        else {
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
exports.parseWorkspace = parseWorkspace;
//# sourceMappingURL=parser.js.map