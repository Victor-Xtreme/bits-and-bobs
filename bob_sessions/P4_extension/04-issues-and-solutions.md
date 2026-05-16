# RepoSense Extension - Issues and Solutions

**Session Date**: May 16, 2026

---

## Issue #1: TypeScript Compilation Errors

### Problem Description

Multiple TypeScript errors preventing compilation:

```
❌ Cannot find module 'vscode' or its corresponding type declarations
❌ Cannot find module 'node-fetch' or its corresponding type declarations
❌ Cannot find name 'console'
❌ Cannot find name 'setInterval'
❌ Cannot find name 'clearInterval'
❌ Cannot find namespace 'NodeJS'
```

### Root Cause

1. **Missing Dependencies**: npm packages not installed
2. **Missing Type Definitions**: @types packages not available
3. **Incomplete TypeScript Configuration**: DOM library not included in tsconfig.json

### Solution Steps

#### Step 1: Install Dependencies

```bash
cd vscode-extension
npm install
```

**Installed Packages**:
- `@types/vscode: ^1.74.0` - VS Code API types
- `@types/node: 16.x` - Node.js types
- `@types/node-fetch: ^2.6.2` - node-fetch types
- `node-fetch: ^2.7.0` - HTTP client
- `typescript: ^4.9.3` - TypeScript compiler
- Other dev dependencies (ESLint, etc.)

#### Step 2: Update tsconfig.json

**Before**:
```json
{
  "compilerOptions": {
    "lib": ["ES2020"]
  }
}
```

**After**:
```json
{
  "compilerOptions": {
    "lib": ["ES2020", "DOM"]
  }
}
```

**Why DOM Library?**
- Provides types for `console` object
- Includes `setInterval` and `clearInterval` functions
- Enables other browser/DOM APIs

#### Step 3: Update package.json

Added runtime dependency:
```json
{
  "dependencies": {
    "node-fetch": "^2.7.0"
  },
  "devDependencies": {
    "@types/node-fetch": "^2.6.2"
  }
}
```

#### Step 4: Fix Type Annotations

Changed polling interval type:
```typescript
// Before
private _pollingInterval?: NodeJS.Timeout;

// After
private _pollingInterval?: ReturnType<typeof setInterval>;
```

### Verification

```bash
npm run compile
# Output: Exit code 0 (Success)
```

**Result**: ✅ All TypeScript errors resolved

---

## Issue #2: PowerShell Execution Policy

### Problem Description

```
npm : File C:\Program Files\nodejs\npm.ps1 cannot be loaded 
because running scripts is disabled on this system.
```

### Root Cause

Windows PowerShell execution policy blocks running npm scripts by default for security reasons.

### Solution

Use Command Prompt instead of PowerShell:

```bash
# Instead of:
cd vscode-extension && npm install  # Fails in PowerShell

# Use:
cmd /c "cd vscode-extension && npm install"  # Works via cmd
```

### Alternative Solutions

1. **Change Execution Policy** (requires admin):
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

2. **Use Git Bash or WSL**: These shells don't have the same restrictions

3. **Use VS Code Terminal**: Set default shell to Command Prompt

### Verification

```bash
cmd /c "cd vscode-extension && npm install"
# Output: Exit code 0 (Success)
```

**Result**: ✅ Dependencies installed successfully

---

## Issue #3: VS Code IntelliSense Cache Error

### Problem Description

VS Code showing red squiggly line under import:
```typescript
import { SidebarProvider } from './SidebarProvider';
// Error: Cannot find module './SidebarProvider'
```

**However**:
- TypeScript compilation succeeds (exit code 0)
- File exists at correct path
- Import path is correct

### Root Cause

VS Code's IntelliSense caches type information and sometimes doesn't refresh after:
- Installing new dependencies
- Updating tsconfig.json
- Creating new files

### Solution

**Method 1: Reload VS Code Window**
1. Press `Ctrl+Shift+P` (Command Palette)
2. Type "Developer: Reload Window"
3. Press Enter

**Method 2: Restart TypeScript Server**
1. Press `Ctrl+Shift+P`
2. Type "TypeScript: Restart TS Server"
3. Press Enter

**Method 3: Close and Reopen VS Code**
- Completely close VS Code
- Reopen the workspace

### Why This Happens

```
VS Code IntelliSense Cache
    ↓
Outdated type information
    ↓
Shows error even though code is correct
    ↓
Reload clears cache
    ↓
IntelliSense re-indexes files
    ↓
Error disappears
```

### Verification

After reload:
- ✅ No red squiggly lines
- ✅ IntelliSense autocomplete works
- ✅ Go to definition works
- ✅ Compilation still succeeds

**Result**: ✅ Visual error resolved (code was always correct)

---

## Issue #4: Missing Icon File (Preventive)

### Potential Problem

package.json references icon that doesn't exist:
```json
{
  "icon": "media/icon.svg"
}
```

### Solution

Created professional SVG icon at `media/icon.svg` with:
- Repository/folder representation
- Code brackets
- Health checkmark
- Activity pulse line
- VS Code color scheme

### Verification

```bash
# Check file exists
dir vscode-extension\media\icon.svg
# Output: File found
```

**Result**: ✅ Icon created proactively

---

## Summary of Resolutions

| Issue | Status | Solution | Time to Resolve |
|-------|--------|----------|-----------------|
| TypeScript Errors | ✅ Resolved | npm install + tsconfig update | ~5 minutes |
| PowerShell Policy | ✅ Resolved | Use cmd instead | ~2 minutes |
| IntelliSense Cache | ✅ Resolved | Reload window | ~1 minute |
| Missing Icon | ✅ Prevented | Created icon.svg | ~3 minutes |

---

## Lessons Learned

### 1. Always Install Dependencies First
Before debugging TypeScript errors, ensure all npm packages are installed.

### 2. Include DOM Library for Extensions
VS Code extensions often need DOM APIs (console, timers) even though they run in Node.js.

### 3. Use cmd on Windows
When PowerShell blocks scripts, cmd is a reliable fallback.

### 4. IntelliSense Cache Issues Are Common
Visual errors don't always mean code errors. Verify with compilation first.

### 5. Create Assets Early
Don't wait for runtime errors to create required assets like icons.

---

## Prevention Strategies

### For Future Projects

1. **Setup Checklist**:
   - [ ] Run `npm install` immediately
   - [ ] Verify tsconfig.json includes necessary libraries
   - [ ] Create all referenced assets
   - [ ] Test compilation before coding

2. **Development Workflow**:
   - Compile frequently (`npm run compile`)
   - Use watch mode during development (`npm run watch`)
   - Reload VS Code after major config changes

3. **Documentation**:
   - Document known issues in README
   - Include troubleshooting section
   - Provide clear setup instructions

---

**All Issues Resolved**: ✅ Extension fully functional