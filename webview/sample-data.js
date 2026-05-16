// Sample data for testing the webview independently
// This simulates the data structure that will come from the backend

const sampleAnalysisData = {
    health: {
        score: 78,
        grade: 'B',
        summary: 'Your codebase is in good shape with room for improvement. Focus on documentation and test coverage to reach the next level.',
        priorities: [
            'Add unit tests for authentication module (currently 45% coverage)',
            'Document public API endpoints in api.js',
            'Fix 2 critical security vulnerabilities in dependencies',
            'Refactor database connection pooling for better performance',
            'Add error handling to async operations in services/'
        ]
    },
    
    architecture: {
        nodes: [
            { id: 'main', label: 'main.js', name: 'main.js', type: 'entry', description: 'Application entry point - initializes server and routes' },
            { id: 'api', label: 'api.js', name: 'api.js', type: 'service', description: 'REST API handler with Express routes' },
            { id: 'auth', label: 'auth.js', name: 'auth.js', type: 'service', description: 'Authentication and authorization logic' },
            { id: 'db', label: 'database.js', name: 'database.js', type: 'service', description: 'Database connection and query builder' },
            { id: 'utils', label: 'utils.js', name: 'utils.js', type: 'util', description: 'Common utility functions' },
            { id: 'logger', label: 'logger.js', name: 'logger.js', type: 'util', description: 'Logging utility with Winston' },
            { id: 'config', label: 'config.js', name: 'config.js', type: 'config', description: 'Application configuration loader' },
            { id: 'test-api', label: 'api.test.js', name: 'api.test.js', type: 'test', description: 'API endpoint tests' },
            { id: 'test-auth', label: 'auth.test.js', name: 'auth.test.js', type: 'test', description: 'Authentication tests' }
        ],
        edges: [
            { source: 'main', target: 'api', relationship: 'imports' },
            { source: 'main', target: 'config', relationship: 'imports' },
            { source: 'api', target: 'auth', relationship: 'calls' },
            { source: 'api', target: 'db', relationship: 'imports' },
            { source: 'api', target: 'logger', relationship: 'imports' },
            { source: 'auth', target: 'db', relationship: 'calls' },
            { source: 'auth', target: 'utils', relationship: 'imports' },
            { source: 'db', target: 'config', relationship: 'imports' },
            { source: 'test-api', target: 'api', relationship: 'imports' },
            { source: 'test-auth', target: 'auth', relationship: 'imports' }
        ]
    },
    
    review: {
        findings: [
            {
                severity: 'CRITICAL',
                file: 'src/auth.js',
                line: 42,
                message: 'Hardcoded API key detected in source code',
                suggestion: 'Move sensitive credentials to environment variables. Use process.env.API_KEY and add to .env file (excluded from git).'
            },
            {
                severity: 'CRITICAL',
                file: 'src/database.js',
                line: 156,
                message: 'SQL injection vulnerability - unsanitized user input',
                suggestion: 'Use parameterized queries or an ORM. Replace string concatenation with prepared statements: db.query("SELECT * FROM users WHERE id = ?", [userId])'
            },
            {
                severity: 'HIGH',
                file: 'src/api.js',
                line: 89,
                message: 'Missing error handling in async function',
                suggestion: 'Wrap async operations in try-catch blocks or use .catch() to handle promise rejections gracefully.'
            },
            {
                severity: 'HIGH',
                file: 'src/utils.js',
                line: 23,
                message: 'Function complexity too high (cyclomatic complexity: 15)',
                suggestion: 'Break down this function into smaller, more focused functions. Consider extracting validation logic into separate helper functions.'
            },
            {
                severity: 'MEDIUM',
                file: 'src/logger.js',
                line: 67,
                message: 'Console.log statement found in production code',
                suggestion: 'Replace console.log with proper logging framework calls. Use logger.info() or logger.debug() instead.'
            },
            {
                severity: 'MEDIUM',
                file: 'src/api.js',
                line: 134,
                message: 'Magic number used without explanation',
                suggestion: 'Extract magic number 3600 to a named constant: const SESSION_TIMEOUT_SECONDS = 3600;'
            },
            {
                severity: 'LOW',
                file: 'src/utils.js',
                line: 45,
                message: 'Variable name "x" is not descriptive',
                suggestion: 'Use descriptive variable names. Rename "x" to something meaningful like "userCount" or "itemIndex".'
            }
        ]
    },
    
    documentation: {
        functions: [
            {
                name: 'authenticateUser(username, password)',
                description: 'Authenticates a user with username and password credentials',
                params: 'username (string): User\'s login name\npassword (string): User\'s password',
                returns: 'Promise<{token: string, user: Object}> - Authentication token and user object',
                example: 'const result = await authenticateUser("john@example.com", "secret123");\nconsole.log(result.token);'
            },
            {
                name: 'queryDatabase(sql, params)',
                description: 'Executes a parameterized SQL query against the database',
                params: 'sql (string): SQL query with ? placeholders\nparams (Array): Array of values to bind to placeholders',
                returns: 'Promise<Array> - Query results as array of objects',
                example: 'const users = await queryDatabase(\n  "SELECT * FROM users WHERE age > ?",\n  [18]\n);'
            },
            {
                name: 'formatDate(date, format)',
                description: 'Formats a date object according to the specified format string',
                params: 'date (Date): Date object to format\nformat (string): Format string (e.g., "YYYY-MM-DD")',
                returns: 'string - Formatted date string',
                example: 'const formatted = formatDate(new Date(), "YYYY-MM-DD");\n// Returns: "2026-05-16"'
            }
        ],
        tests: [
            {
                name: 'Test: authenticateUser with valid credentials',
                code: `describe('authenticateUser', () => {
  it('should return token for valid credentials', async () => {
    const result = await authenticateUser('test@example.com', 'password123');
    expect(result).toHaveProperty('token');
    expect(result).toHaveProperty('user');
    expect(result.user.email).toBe('test@example.com');
  });
  
  it('should throw error for invalid credentials', async () => {
    await expect(
      authenticateUser('test@example.com', 'wrongpassword')
    ).rejects.toThrow('Invalid credentials');
  });
});`
            },
            {
                name: 'Test: queryDatabase with parameterized query',
                code: `describe('queryDatabase', () => {
  it('should execute parameterized query safely', async () => {
    const results = await queryDatabase(
      'SELECT * FROM users WHERE age > ?',
      [18]
    );
    expect(Array.isArray(results)).toBe(true);
    results.forEach(user => {
      expect(user.age).toBeGreaterThan(18);
    });
  });
});`
            }
        ]
    },
    
    security: {
        issues: [
            {
                title: 'Outdated dependency: express@4.16.0',
                description: 'Express version 4.16.0 has known security vulnerabilities (CVE-2022-24999). Update to version 4.18.0 or later.',
                effort: 'LOW'
            },
            {
                title: 'Missing rate limiting on API endpoints',
                description: 'API endpoints are vulnerable to brute force attacks. Implement rate limiting using express-rate-limit middleware.',
                effort: 'MEDIUM'
            },
            {
                title: 'Weak password hashing algorithm',
                description: 'Using MD5 for password hashing. Switch to bcrypt with salt rounds >= 10 for secure password storage.',
                effort: 'HIGH'
            },
            {
                title: 'CORS policy too permissive',
                description: 'CORS is set to allow all origins (*). Restrict to specific trusted domains in production.',
                effort: 'LOW'
            }
        ],
        modernization: [
            {
                title: 'Migrate from callbacks to async/await',
                description: 'Several modules still use callback-based patterns. Modernize to async/await for better readability and error handling.',
                effort: 'MEDIUM'
            },
            {
                title: 'Replace var with const/let',
                description: 'Found 23 instances of var declarations. Use const for immutable values and let for mutable ones.',
                effort: 'LOW'
            },
            {
                title: 'Add TypeScript for type safety',
                description: 'Consider migrating to TypeScript to catch type errors at compile time and improve IDE support.',
                effort: 'HIGH'
            },
            {
                title: 'Implement ES6 modules',
                description: 'Currently using CommonJS (require/module.exports). Migrate to ES6 import/export syntax.',
                effort: 'MEDIUM'
            }
        ]
    }
};

// Function to simulate receiving data from extension
function simulateExtensionMessage(delay = 1000) {
    // Simulate loading
    window.postMessage({ type: 'loading', step: 'Initializing analysis...' }, '*');
    
    setTimeout(() => {
        window.postMessage({ type: 'progress', data: { percentage: 25, step: 'Parsing files...' } }, '*');
    }, delay * 0.25);
    
    setTimeout(() => {
        window.postMessage({ type: 'progress', data: { percentage: 50, step: 'Analyzing code structure...' } }, '*');
    }, delay * 0.5);
    
    setTimeout(() => {
        window.postMessage({ type: 'progress', data: { percentage: 75, step: 'Running security checks...' } }, '*');
    }, delay * 0.75);
    
    setTimeout(() => {
        window.postMessage({ type: 'results', data: sampleAnalysisData }, '*');
    }, delay);
}

// Uncomment to auto-load sample data when page loads
// window.addEventListener('load', () => {
//     setTimeout(() => simulateExtensionMessage(2000), 500);
// });

// Made with Bob
