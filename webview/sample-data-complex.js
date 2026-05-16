// Complex sample data for testing the dependency tree with deeper hierarchies
// This simulates a larger, more realistic codebase structure

const complexAnalysisData = {
    health: {
        score: 68,
        grade: 'C',
        summary: 'Your codebase shows signs of technical debt and architectural complexity. Focus on refactoring core modules and improving test coverage to reach the next level.',
        priorities: [
            'Refactor UserService class - cyclomatic complexity of 28 (target: <10)',
            'Add integration tests for payment processing module (0% coverage)',
            'Fix 5 critical security vulnerabilities in authentication flow',
            'Document API endpoints in controllers/ directory (12 undocumented endpoints)',
            'Migrate legacy callback-based code to async/await (47 files affected)',
            'Reduce circular dependencies between services and models layers',
            'Update 8 outdated dependencies with known CVEs'
        ]
    },
    
    architecture: {
        nodes: [
            // Entry points
            { id: 'src/index.ts', label: 'index.ts', name: 'index.ts', type: 'entry', description: 'Application entry point - bootstraps Express server and initializes middleware' },
            { id: 'src/server.ts', label: 'server.ts', name: 'server.ts', type: 'entry', description: 'HTTP server configuration and startup logic' },
            
            // Controllers (service layer)
            { id: 'src/controllers/UserController.ts', label: 'UserController', name: 'UserController.ts', type: 'service', description: 'Handles user CRUD operations and profile management' },
            { id: 'src/controllers/AuthController.ts', label: 'AuthController', name: 'AuthController.ts', type: 'service', description: 'Authentication endpoints - login, logout, token refresh' },
            { id: 'src/controllers/PaymentController.ts', label: 'PaymentController', name: 'PaymentController.ts', type: 'service', description: 'Payment processing and transaction management' },
            { id: 'src/controllers/OrderController.ts', label: 'OrderController', name: 'OrderController.ts', type: 'service', description: 'Order creation, tracking, and fulfillment' },
            
            // Services (business logic)
            { id: 'src/services/UserService.ts', label: 'UserService', name: 'UserService.ts', type: 'service', description: 'User business logic and validation' },
            { id: 'src/services/AuthService.ts', label: 'AuthService', name: 'AuthService.ts', type: 'service', description: 'JWT token generation and validation' },
            { id: 'src/services/PaymentService.ts', label: 'PaymentService', name: 'PaymentService.ts', type: 'service', description: 'Stripe integration and payment processing' },
            { id: 'src/services/EmailService.ts', label: 'EmailService', name: 'EmailService.ts', type: 'service', description: 'Email notifications via SendGrid' },
            { id: 'src/services/NotificationService.ts', label: 'NotificationService', name: 'NotificationService.ts', type: 'service', description: 'Push notifications and in-app alerts' },
            
            // Models (data layer)
            { id: 'src/models/User.ts', label: 'User', name: 'User.ts', type: 'service', description: 'User data model and database schema' },
            { id: 'src/models/Order.ts', label: 'Order', name: 'Order.ts', type: 'service', description: 'Order data model with relationships' },
            { id: 'src/models/Payment.ts', label: 'Payment', name: 'Payment.ts', type: 'service', description: 'Payment transaction records' },
            
            // Middleware
            { id: 'src/middleware/auth.ts', label: 'auth middleware', name: 'auth.ts', type: 'service', description: 'JWT authentication middleware' },
            { id: 'src/middleware/validation.ts', label: 'validation', name: 'validation.ts', type: 'service', description: 'Request validation middleware' },
            { id: 'src/middleware/errorHandler.ts', label: 'errorHandler', name: 'errorHandler.ts', type: 'service', description: 'Global error handling middleware' },
            
            // Database
            { id: 'src/database/connection.ts', label: 'DB connection', name: 'connection.ts', type: 'service', description: 'PostgreSQL connection pool manager' },
            { id: 'src/database/migrations.ts', label: 'migrations', name: 'migrations.ts', type: 'service', description: 'Database migration runner' },
            
            // Utilities
            { id: 'src/utils/logger.ts', label: 'logger', name: 'logger.ts', type: 'util', description: 'Winston-based logging utility' },
            { id: 'src/utils/validator.ts', label: 'validator', name: 'validator.ts', type: 'util', description: 'Input validation helpers' },
            { id: 'src/utils/crypto.ts', label: 'crypto', name: 'crypto.ts', type: 'util', description: 'Encryption and hashing utilities' },
            { id: 'src/utils/dateHelper.ts', label: 'dateHelper', name: 'dateHelper.ts', type: 'util', description: 'Date formatting and timezone utilities' },
            
            // Config
            { id: 'src/config/database.ts', label: 'DB config', name: 'database.ts', type: 'config', description: 'Database connection configuration' },
            { id: 'src/config/app.ts', label: 'app config', name: 'app.ts', type: 'config', description: 'Application-wide configuration' },
            { id: 'src/config/env.ts', label: 'env', name: 'env.ts', type: 'config', description: 'Environment variable loader' },
            
            // Tests
            { id: 'tests/unit/UserService.test.ts', label: 'UserService.test', name: 'UserService.test.ts', type: 'test', description: 'Unit tests for UserService' },
            { id: 'tests/unit/AuthService.test.ts', label: 'AuthService.test', name: 'AuthService.test.ts', type: 'test', description: 'Unit tests for AuthService' },
            { id: 'tests/integration/auth.test.ts', label: 'auth.test', name: 'auth.test.ts', type: 'test', description: 'Integration tests for auth flow' },
            { id: 'tests/integration/payment.test.ts', label: 'payment.test', name: 'payment.test.ts', type: 'test', description: 'Integration tests for payment processing' },
            { id: 'tests/e2e/checkout.test.ts', label: 'checkout.test', name: 'checkout.test.ts', type: 'test', description: 'End-to-end checkout flow tests' }
        ],
        
        edges: [
            // Entry point dependencies
            { source: 'src/index.ts', target: 'src/server.ts', relationship: 'imports' },
            { source: 'src/index.ts', target: 'src/config/app.ts', relationship: 'imports' },
            { source: 'src/index.ts', target: 'src/database/connection.ts', relationship: 'calls' },
            { source: 'src/index.ts', target: 'src/utils/logger.ts', relationship: 'imports' },
            
            { source: 'src/server.ts', target: 'src/controllers/UserController.ts', relationship: 'imports' },
            { source: 'src/server.ts', target: 'src/controllers/AuthController.ts', relationship: 'imports' },
            { source: 'src/server.ts', target: 'src/controllers/PaymentController.ts', relationship: 'imports' },
            { source: 'src/server.ts', target: 'src/controllers/OrderController.ts', relationship: 'imports' },
            { source: 'src/server.ts', target: 'src/middleware/auth.ts', relationship: 'imports' },
            { source: 'src/server.ts', target: 'src/middleware/errorHandler.ts', relationship: 'imports' },
            
            // Controller to Service dependencies
            { source: 'src/controllers/UserController.ts', target: 'src/services/UserService.ts', relationship: 'calls' },
            { source: 'src/controllers/UserController.ts', target: 'src/middleware/validation.ts', relationship: 'imports' },
            { source: 'src/controllers/UserController.ts', target: 'src/utils/logger.ts', relationship: 'imports' },
            
            { source: 'src/controllers/AuthController.ts', target: 'src/services/AuthService.ts', relationship: 'calls' },
            { source: 'src/controllers/AuthController.ts', target: 'src/services/UserService.ts', relationship: 'calls' },
            { source: 'src/controllers/AuthController.ts', target: 'src/utils/logger.ts', relationship: 'imports' },
            
            { source: 'src/controllers/PaymentController.ts', target: 'src/services/PaymentService.ts', relationship: 'calls' },
            { source: 'src/controllers/PaymentController.ts', target: 'src/services/EmailService.ts', relationship: 'calls' },
            { source: 'src/controllers/PaymentController.ts', target: 'src/middleware/auth.ts', relationship: 'imports' },
            
            { source: 'src/controllers/OrderController.ts', target: 'src/services/PaymentService.ts', relationship: 'calls' },
            { source: 'src/controllers/OrderController.ts', target: 'src/services/NotificationService.ts', relationship: 'calls' },
            { source: 'src/controllers/OrderController.ts', target: 'src/models/Order.ts', relationship: 'imports' },
            
            // Service to Model dependencies
            { source: 'src/services/UserService.ts', target: 'src/models/User.ts', relationship: 'imports' },
            { source: 'src/services/UserService.ts', target: 'src/utils/validator.ts', relationship: 'imports' },
            { source: 'src/services/UserService.ts', target: 'src/utils/crypto.ts', relationship: 'calls' },
            { source: 'src/services/UserService.ts', target: 'src/database/connection.ts', relationship: 'calls' },
            
            { source: 'src/services/AuthService.ts', target: 'src/models/User.ts', relationship: 'imports' },
            { source: 'src/services/AuthService.ts', target: 'src/utils/crypto.ts', relationship: 'calls' },
            { source: 'src/services/AuthService.ts', target: 'src/config/app.ts', relationship: 'imports' },
            
            { source: 'src/services/PaymentService.ts', target: 'src/models/Payment.ts', relationship: 'imports' },
            { source: 'src/services/PaymentService.ts', target: 'src/models/Order.ts', relationship: 'imports' },
            { source: 'src/services/PaymentService.ts', target: 'src/utils/logger.ts', relationship: 'imports' },
            { source: 'src/services/PaymentService.ts', target: 'src/config/app.ts', relationship: 'imports' },
            
            { source: 'src/services/EmailService.ts', target: 'src/utils/logger.ts', relationship: 'imports' },
            { source: 'src/services/EmailService.ts', target: 'src/config/app.ts', relationship: 'imports' },
            
            { source: 'src/services/NotificationService.ts', target: 'src/models/User.ts', relationship: 'imports' },
            { source: 'src/services/NotificationService.ts', target: 'src/utils/logger.ts', relationship: 'imports' },
            
            // Model dependencies
            { source: 'src/models/User.ts', target: 'src/database/connection.ts', relationship: 'imports' },
            { source: 'src/models/User.ts', target: 'src/utils/dateHelper.ts', relationship: 'imports' },
            
            { source: 'src/models/Order.ts', target: 'src/database/connection.ts', relationship: 'imports' },
            { source: 'src/models/Order.ts', target: 'src/models/User.ts', relationship: 'imports' },
            { source: 'src/models/Order.ts', target: 'src/models/Payment.ts', relationship: 'imports' },
            
            { source: 'src/models/Payment.ts', target: 'src/database/connection.ts', relationship: 'imports' },
            { source: 'src/models/Payment.ts', target: 'src/utils/dateHelper.ts', relationship: 'imports' },
            
            // Middleware dependencies
            { source: 'src/middleware/auth.ts', target: 'src/services/AuthService.ts', relationship: 'calls' },
            { source: 'src/middleware/auth.ts', target: 'src/utils/logger.ts', relationship: 'imports' },
            
            { source: 'src/middleware/validation.ts', target: 'src/utils/validator.ts', relationship: 'imports' },
            { source: 'src/middleware/validation.ts', target: 'src/utils/logger.ts', relationship: 'imports' },
            
            { source: 'src/middleware/errorHandler.ts', target: 'src/utils/logger.ts', relationship: 'imports' },
            
            // Database dependencies
            { source: 'src/database/connection.ts', target: 'src/config/database.ts', relationship: 'imports' },
            { source: 'src/database/connection.ts', target: 'src/utils/logger.ts', relationship: 'imports' },
            
            { source: 'src/database/migrations.ts', target: 'src/database/connection.ts', relationship: 'imports' },
            { source: 'src/database/migrations.ts', target: 'src/utils/logger.ts', relationship: 'imports' },
            
            // Config dependencies
            { source: 'src/config/database.ts', target: 'src/config/env.ts', relationship: 'imports' },
            { source: 'src/config/app.ts', target: 'src/config/env.ts', relationship: 'imports' },
            
            // Test dependencies
            { source: 'tests/unit/UserService.test.ts', target: 'src/services/UserService.ts', relationship: 'imports' },
            { source: 'tests/unit/UserService.test.ts', target: 'src/models/User.ts', relationship: 'imports' },
            
            { source: 'tests/unit/AuthService.test.ts', target: 'src/services/AuthService.ts', relationship: 'imports' },
            
            { source: 'tests/integration/auth.test.ts', target: 'src/controllers/AuthController.ts', relationship: 'imports' },
            { source: 'tests/integration/auth.test.ts', target: 'src/server.ts', relationship: 'imports' },
            
            { source: 'tests/integration/payment.test.ts', target: 'src/controllers/PaymentController.ts', relationship: 'imports' },
            { source: 'tests/integration/payment.test.ts', target: 'src/services/PaymentService.ts', relationship: 'imports' },
            
            { source: 'tests/e2e/checkout.test.ts', target: 'src/server.ts', relationship: 'imports' }
        ]
    },
    
    review: {
        findings: [
            {
                severity: 'CRITICAL',
                file: 'src/services/AuthService.ts',
                line: 67,
                message: 'JWT secret key hardcoded in source code',
                suggestion: 'Move JWT_SECRET to environment variables. Use process.env.JWT_SECRET and add to .env file (excluded from git). Never commit secrets to version control.'
            },
            {
                severity: 'CRITICAL',
                file: 'src/controllers/PaymentController.ts',
                line: 134,
                message: 'SQL injection vulnerability - user input concatenated directly into query',
                suggestion: 'Use parameterized queries or ORM. Replace: `SELECT * FROM payments WHERE user_id = ${userId}` with prepared statement: db.query("SELECT * FROM payments WHERE user_id = $1", [userId])'
            },
            {
                severity: 'CRITICAL',
                file: 'src/middleware/auth.ts',
                line: 23,
                message: 'Authentication bypass - missing token validation in production',
                suggestion: 'Remove the NODE_ENV === "development" bypass. Always validate tokens in all environments. Use feature flags for testing instead.'
            },
            {
                severity: 'HIGH',
                file: 'src/services/UserService.ts',
                line: 89,
                message: 'Cyclomatic complexity of 28 exceeds threshold of 10',
                suggestion: 'Break down validateUserData() into smaller functions: validateEmail(), validatePassword(), validateProfile(). Extract business rules into separate validator classes.'
            },
            {
                severity: 'HIGH',
                file: 'src/services/PaymentService.ts',
                line: 156,
                message: 'Unhandled promise rejection in async payment processing',
                suggestion: 'Wrap stripe.charges.create() in try-catch block. Log errors and return appropriate error response. Consider implementing retry logic for transient failures.'
            },
            {
                severity: 'HIGH',
                file: 'src/models/Order.ts',
                line: 45,
                message: 'Circular dependency detected between Order and Payment models',
                suggestion: 'Refactor to use dependency injection or create a shared interface. Consider moving shared types to a separate types.ts file.'
            },
            {
                severity: 'MEDIUM',
                file: 'src/utils/logger.ts',
                line: 34,
                message: 'Console.log statements found in production code',
                suggestion: 'Replace all console.log with logger.info() or logger.debug(). Configure log levels per environment in config.'
            },
            {
                severity: 'MEDIUM',
                file: 'src/controllers/UserController.ts',
                line: 78,
                message: 'Missing input validation for email parameter',
                suggestion: 'Add email format validation using validator library or regex. Return 400 Bad Request for invalid input before processing.'
            },
            {
                severity: 'MEDIUM',
                file: 'src/database/connection.ts',
                line: 23,
                message: 'Database connection pool not properly closed on shutdown',
                suggestion: 'Implement graceful shutdown handler. Listen for SIGTERM/SIGINT and call pool.end() before process exit.'
            },
            {
                severity: 'LOW',
                file: 'src/services/EmailService.ts',
                line: 56,
                message: 'Magic number 3600 used without explanation',
                suggestion: 'Extract to named constant: const EMAIL_RETRY_DELAY_SECONDS = 3600; Improves code readability and maintainability.'
            },
            {
                severity: 'LOW',
                file: 'src/utils/validator.ts',
                line: 12,
                message: 'Variable name "x" is not descriptive',
                suggestion: 'Rename to something meaningful like "validationResult" or "isValid". Descriptive names improve code readability.'
            }
        ]
    },
    
    documentation: {
        functions: [
            {
                name: 'UserService.createUser(userData)',
                description: 'Creates a new user account with validation and password hashing',
                params: 'userData (UserCreateDTO): Object containing email, password, name, and optional profile fields',
                returns: 'Promise<User> - Created user object with hashed password and generated ID',
                example: 'const user = await userService.createUser({\n  email: "john@example.com",\n  password: "SecurePass123!",\n  name: "John Doe"\n});'
            },
            {
                name: 'AuthService.generateToken(userId, role)',
                description: 'Generates a JWT access token for authenticated user',
                params: 'userId (string): User\'s unique identifier\nrole (string): User role for authorization',
                returns: 'Promise<string> - Signed JWT token valid for 24 hours',
                example: 'const token = await authService.generateToken(\n  user.id,\n  user.role\n);\nres.json({ token });'
            },
            {
                name: 'PaymentService.processPayment(orderId, paymentMethod)',
                description: 'Processes payment through Stripe and updates order status',
                params: 'orderId (string): Order ID to process payment for\npaymentMethod (PaymentMethod): Stripe payment method object',
                returns: 'Promise<PaymentResult> - Payment confirmation with transaction ID',
                example: 'const result = await paymentService.processPayment(\n  order.id,\n  stripePaymentMethod\n);\nif (result.success) {\n  await orderService.markAsPaid(order.id);\n}'
            }
        ],
        tests: [
            {
                name: 'Test: UserService.createUser with valid data',
                code: `describe('UserService.createUser', () => {
  it('should create user with hashed password', async () => {
    const userData = {
      email: 'test@example.com',
      password: 'SecurePass123!',
      name: 'Test User'
    };
    
    const user = await userService.createUser(userData);
    
    expect(user).toHaveProperty('id');
    expect(user.email).toBe(userData.email);
    expect(user.password).not.toBe(userData.password); // Should be hashed
    expect(user.password).toMatch(/^\$2[aby]\$/); // bcrypt format
  });
  
  it('should throw error for duplicate email', async () => {
    const userData = { email: 'existing@example.com', password: 'pass', name: 'User' };
    
    await expect(
      userService.createUser(userData)
    ).rejects.toThrow('Email already exists');
  });
});`
            },
            {
                name: 'Test: PaymentService.processPayment integration',
                code: `describe('PaymentService.processPayment', () => {
  it('should process payment and update order', async () => {
    const order = await createTestOrder();
    const paymentMethod = await createTestPaymentMethod();
    
    const result = await paymentService.processPayment(
      order.id,
      paymentMethod
    );
    
    expect(result.success).toBe(true);
    expect(result.transactionId).toBeDefined();
    
    const updatedOrder = await orderService.getById(order.id);
    expect(updatedOrder.status).toBe('paid');
  });
});`
            }
        ]
    },
    
    security: {
        issues: [
            {
                title: 'Critical: JWT secret exposed in source code',
                description: 'The JWT signing secret is hardcoded in AuthService.ts. This allows anyone with access to the code to forge authentication tokens. Move to environment variables immediately.',
                effort: 'LOW'
            },
            {
                title: 'SQL injection in payment queries',
                description: 'User input is directly concatenated into SQL queries in PaymentController. This allows attackers to execute arbitrary SQL commands. Use parameterized queries or an ORM.',
                effort: 'MEDIUM'
            },
            {
                title: 'Missing rate limiting on authentication endpoints',
                description: 'Login and registration endpoints have no rate limiting, making them vulnerable to brute force attacks. Implement express-rate-limit middleware.',
                effort: 'LOW'
            },
            {
                title: 'Outdated dependencies with known CVEs',
                description: 'express@4.16.0 (CVE-2022-24999), jsonwebtoken@8.5.0 (CVE-2022-23529), and 6 other packages have security vulnerabilities. Run npm audit fix.',
                effort: 'LOW'
            },
            {
                title: 'Weak password hashing algorithm',
                description: 'Using MD5 for password hashing in legacy code paths. MD5 is cryptographically broken. Migrate all passwords to bcrypt with salt rounds >= 12.',
                effort: 'HIGH'
            },
            {
                title: 'CORS policy allows all origins',
                description: 'CORS is configured with origin: "*" in production. This allows any website to make requests to your API. Restrict to specific trusted domains.',
                effort: 'LOW'
            },
            {
                title: 'Sensitive data logged in production',
                description: 'User passwords and payment details are being logged in error messages. Sanitize logs to remove PII and sensitive data before logging.',
                effort: 'MEDIUM'
            }
        ],
        modernization: [
            {
                title: 'Migrate from callbacks to async/await',
                description: 'Database queries and external API calls still use callback patterns in 23 files. Modernize to async/await for better error handling and readability.',
                effort: 'MEDIUM'
            },
            {
                title: 'Replace var with const/let',
                description: 'Found 47 instances of var declarations across the codebase. Use const for immutable values and let for mutable ones to prevent scope issues.',
                effort: 'LOW'
            },
            {
                title: 'Add TypeScript strict mode',
                description: 'TypeScript is configured with loose type checking. Enable strict mode to catch more errors at compile time and improve type safety.',
                effort: 'MEDIUM'
            },
            {
                title: 'Implement dependency injection',
                description: 'Services are tightly coupled with direct imports. Implement DI container (e.g., tsyringe) for better testability and modularity.',
                effort: 'HIGH'
            },
            {
                title: 'Migrate to ES6 modules',
                description: 'Currently using CommonJS (require/module.exports). Migrate to ES6 import/export syntax for better tree-shaking and modern tooling support.',
                effort: 'MEDIUM'
            },
            {
                title: 'Add API versioning',
                description: 'API endpoints have no versioning strategy. Implement /api/v1/ prefix to allow backward-compatible changes in the future.',
                effort: 'LOW'
            }
        ]
    }
};

// Export for use in test files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { complexAnalysisData };
}

// Made with Bob
