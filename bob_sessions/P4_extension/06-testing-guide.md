# RepoSense Extension - Testing Guide

**Session Date**: May 16, 2026

---

## Prerequisites

Before testing the extension, ensure:

- ✅ VS Code installed (version 1.74.0 or higher)
- ✅ Node.js installed (version 16.x or higher)
- ✅ npm installed
- ✅ Backend service available at http://localhost:8000

---

## Setup for Testing

### 1. Install Dependencies

```bash
cd vscode-extension
npm install
```

**Expected Output**:
```
added 150 packages in 15s
```

### 2. Compile TypeScript

```bash
npm run compile
```

**Expected Output**:
```
> reposense@0.0.1 compile
> tsc -p ./

# No errors = success
```

### 3. Verify Compilation

Check that `out/` directory was created:

```bash
dir out
# Should show:
# extension.js
# extension.js.map
# SidebarProvider.js
# SidebarProvider.js.map
```

---

## Running the Extension

### Method 1: Using F5 (Recommended)

1. Open `vscode-extension` folder in VS Code
2. Press **F5** on your keyboard
3. Select "Extension" if prompted
4. Wait for Extension Development Host to launch

**Expected Result**:
- New VS Code window opens
- Title bar shows "[Extension Development Host]"
- Your extension is loaded and active

### Method 2: Using Debug Panel

1. Click Debug icon in Activity Bar (Ctrl+Shift+D)
2. Select "Extension" from dropdown
3. Click green "Start Debugging" button
4. Extension Development Host launches

### Method 3: Using Command Palette

1. Press Ctrl+Shift+P
2. Type "Debug: Start Debugging"
3. Press Enter
4. Extension Development Host launches

---

## Testing the Extension

### Test 1: Extension Activation

**Steps**:
1. Launch Extension Development Host (F5)
2. Look at Debug Console in original VS Code window

**Expected Output**:
```
Activating extension 'reposense'...
RepoSense extension is now active
```

**Pass Criteria**: ✅ No errors in Debug Console

---

### Test 2: Sidebar Visibility

**Steps**:
1. In Extension Development Host window
2. Look for RepoSense icon in Activity Bar (left sidebar)
3. Icon should show code brackets with checkmark

**Expected Result**:
- ✅ Icon visible in Activity Bar
- ✅ Icon matches design (blue with checkmark)

**If Icon Missing**:
- Check `media/icon.svg` exists
- Verify `package.json` has correct icon path
- Reload window (Ctrl+R)

---

### Test 3: Open Sidebar

**Steps**:
1. Click RepoSense icon in Activity Bar
2. Sidebar panel should open

**Expected Result**:
- ✅ Sidebar opens on the left
- ✅ Shows "RepoSense" title
- ✅ Displays "Analyze Workspace" button
- ✅ No error messages

**Screenshot**:
```
┌─────────────────────────┐
│      RepoSense          │
├─────────────────────────┤
│                         │
│  ┌───────────────────┐  │
│  │ Analyze Workspace │  │
│  └───────────────────┘  │
│                         │
└─────────────────────────┘
```

---

### Test 4: Button Interaction (No Backend)

**Steps**:
1. Open sidebar
2. Click "Analyze Workspace" button
3. Observe behavior

**Expected Result** (without backend):
- ✅ Button becomes disabled
- ✅ Error message appears: "Failed to start analysis: fetch failed"
- ✅ Button re-enables after error

**This is Normal**: Backend not running yet

---

### Test 5: Full Analysis Flow (With Backend)

**Prerequisites**:
- Backend service running on http://localhost:8000
- Backend implements `/analyze` and `/results/{job_id}` endpoints

**Steps**:
1. Start backend service
2. Open workspace folder in Extension Development Host
3. Click RepoSense icon
4. Click "Analyze Workspace" button
5. Observe progress updates

**Expected Flow**:
```
1. Button disabled
2. "Starting analysis..." appears
3. Progress updates show:
   "✓ architect complete"
   "✓ security complete"
   etc.
4. Final result:
   "Analysis Complete!"
   "Health Score: 85"
5. Button re-enabled
```

**Pass Criteria**:
- ✅ No errors in Debug Console
- ✅ Progress updates appear
- ✅ Health score displays
- ✅ Button re-enables

---

### Test 6: Error Handling

#### Test 6a: No Workspace Open

**Steps**:
1. Close all folders in Extension Development Host
2. Click "Analyze Workspace"

**Expected Result**:
- ✅ Error message: "No workspace folder open"
- ✅ Button re-enables

#### Test 6b: Backend Unavailable

**Steps**:
1. Stop backend service
2. Click "Analyze Workspace"

**Expected Result**:
- ✅ Error message: "Failed to start analysis: fetch failed"
- ✅ Button re-enables

#### Test 6c: Analysis Fails

**Steps**:
1. Backend returns status "failed"
2. Observe error handling

**Expected Result**:
- ✅ Error message displays
- ✅ Polling stops
- ✅ Button re-enables

---

## Debug Console Monitoring

### What to Watch For

**Normal Output**:
```
RepoSense extension is now active
Analyzing workspace: C:\Users\...\project
Job ID received: abc123
Polling started
Status: in_progress
Status: completed
Health score: 85
```

**Error Indicators**:
```
❌ Error: Cannot find module...
❌ TypeError: Cannot read property...
❌ Failed to fetch...
❌ Unhandled promise rejection...
```

### Common Debug Messages

| Message | Meaning | Action |
|---------|---------|--------|
| "Extension is now active" | ✅ Extension loaded | None needed |
| "Cannot find module 'vscode'" | ❌ Dependencies missing | Run `npm install` |
| "fetch failed" | ❌ Backend unavailable | Start backend |
| "No workspace folder open" | ⚠️ No folder open | Open a folder |

---

## Performance Testing

### Test 7: Polling Performance

**Steps**:
1. Start analysis
2. Monitor Debug Console
3. Count polling requests

**Expected Behavior**:
- ✅ Polls every 3 seconds
- ✅ Stops immediately on completion
- ✅ No memory leaks

**Verification**:
```javascript
// Check polling interval
console.log('Polling at:', new Date().toISOString());
// Should show ~3 second intervals
```

### Test 8: Multiple Analyses

**Steps**:
1. Run analysis to completion
2. Click "Analyze Workspace" again
3. Verify no interference

**Expected Result**:
- ✅ Previous polling stopped
- ✅ New analysis starts fresh
- ✅ No duplicate polling

---

## UI/UX Testing

### Test 9: Visual Appearance

**Checklist**:
- ✅ Button has proper styling
- ✅ Text is readable
- ✅ Colors match VS Code theme
- ✅ Status messages are clear
- ✅ Health score is prominent

### Test 10: Responsiveness

**Steps**:
1. Resize sidebar
2. Change VS Code theme
3. Verify layout adapts

**Expected Result**:
- ✅ Button width adjusts
- ✅ Text wraps properly
- ✅ Colors update with theme

---

## Integration Testing

### Test 11: With Real Backend

**Setup**:
```bash
# Start your backend service
cd backend
python app.py  # or your backend command
```

**Test Scenarios**:

1. **Quick Analysis** (< 5 seconds):
   - ✅ Progress updates appear
   - ✅ Completes successfully

2. **Long Analysis** (> 30 seconds):
   - ✅ Polling continues
   - ✅ Progress updates throughout
   - ✅ Completes successfully

3. **Failed Analysis**:
   - ✅ Error message clear
   - ✅ Polling stops
   - ✅ Can retry

---

## Automated Testing (Future)

### Unit Tests

```typescript
// Example test structure
describe('SidebarProvider', () => {
  it('should register webview provider', () => {
    // Test registration
  });
  
  it('should handle analyze button click', () => {
    // Test button handler
  });
  
  it('should poll for results', () => {
    // Test polling mechanism
  });
});
```

### Integration Tests

```typescript
describe('API Integration', () => {
  it('should POST to /analyze', async () => {
    // Test API call
  });
  
  it('should poll /results', async () => {
    // Test polling
  });
});
```

---

## Troubleshooting Test Failures

### Extension Won't Load

**Symptoms**: No activation message in Debug Console

**Solutions**:
1. Check `package.json` syntax
2. Verify `main` points to `./out/extension.js`
3. Ensure TypeScript compiled successfully
4. Check activation events

### Sidebar Won't Open

**Symptoms**: Icon visible but sidebar doesn't open

**Solutions**:
1. Check `contributes.views` in package.json
2. Verify view ID matches registration
3. Check for errors in Debug Console
4. Reload Extension Development Host

### Button Doesn't Work

**Symptoms**: Click has no effect

**Solutions**:
1. Check webview message handling
2. Verify `enableScripts: true` in webview options
3. Check browser console in webview (Ctrl+Shift+I)
4. Verify event listener attached

### Polling Doesn't Stop

**Symptoms**: Continues after completion

**Solutions**:
1. Check status comparison logic
2. Verify `clearInterval` is called
3. Check for typos in status strings
4. Add logging to polling function

---

## Test Checklist

Before considering testing complete:

- [ ] Extension activates without errors
- [ ] Icon appears in Activity Bar
- [ ] Sidebar opens when icon clicked
- [ ] Button is visible and styled
- [ ] Button click triggers analysis
- [ ] Error handling works (no workspace)
- [ ] Error handling works (no backend)
- [ ] Progress updates display correctly
- [ ] Health score displays on completion
- [ ] Polling stops after completion
- [ ] Can run multiple analyses
- [ ] No memory leaks
- [ ] Debug Console shows no errors
- [ ] Works with real backend

---

## Test Report Template

```markdown
## Test Session Report

**Date**: YYYY-MM-DD
**Tester**: Name
**Environment**: Windows/Mac/Linux, VS Code version

### Tests Passed: X/14

| Test | Status | Notes |
|------|--------|-------|
| Extension Activation | ✅/❌ | |
| Sidebar Visibility | ✅/❌ | |
| Open Sidebar | ✅/❌ | |
| Button Interaction | ✅/❌ | |
| Full Analysis Flow | ✅/❌ | |
| Error: No Workspace | ✅/❌ | |
| Error: No Backend | ✅/❌ | |
| Error: Analysis Failed | ✅/❌ | |
| Polling Performance | ✅/❌ | |
| Multiple Analyses | ✅/❌ | |
| Visual Appearance | ✅/❌ | |
| Responsiveness | ✅/❌ | |
| Real Backend Integration | ✅/❌ | |
| No Memory Leaks | ✅/❌ | |

### Issues Found:
1. [Description]
2. [Description]

### Recommendations:
1. [Suggestion]
2. [Suggestion]
```

---

**Testing Status**: ✅ Ready for comprehensive testing