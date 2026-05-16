# RepoSense Extension - Deployment Guide

**Session Date**: May 16, 2026

---

## Deployment Options

1. **Local Development** - Testing and development
2. **VSIX Package** - Shareable installation file
3. **VS Code Marketplace** - Public distribution
4. **Private Registry** - Enterprise distribution

---

## Option 1: Local Development

### For Testing and Development

**Current Status**: ✅ Already set up

**Usage**:
```bash
cd vscode-extension
npm install
npm run compile
# Press F5 in VS Code
```

**Pros**:
- Instant testing
- Easy debugging
- No packaging needed

**Cons**:
- Only available in development mode
- Not shareable

---

## Option 2: VSIX Package

### Create Installable Package

#### Step 1: Install vsce

```bash
npm install -g @vscode/vsce
```

#### Step 2: Prepare for Packaging

Ensure these files exist:
- ✅ README.md
- ✅ LICENSE (create if needed)
- ✅ CHANGELOG.md (optional)
- ✅ Icon (media/icon.svg)

#### Step 3: Create Package

```bash
cd vscode-extension
vsce package
```

**Output**:
```
Executing prepublish script 'npm run vscode:prepublish'...
Packaging extension...
Created: reposense-0.0.1.vsix
```

#### Step 4: Install VSIX

**Method A: Command Line**
```bash
code --install-extension reposense-0.0.1.vsix
```

**Method B: VS Code UI**
1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Click `...` menu
4. Select "Install from VSIX..."
5. Choose `reposense-0.0.1.vsix`

#### Step 5: Verify Installation

1. Restart VS Code
2. Look for RepoSense icon in Activity Bar
3. Extension should work normally

### Sharing VSIX

**Distribution Methods**:
- Email attachment
- File sharing service (Dropbox, Google Drive)
- Internal company server
- GitHub releases

**Installation Instructions for Users**:
```markdown
1. Download reposense-0.0.1.vsix
2. Open VS Code
3. Press Ctrl+Shift+X (Extensions)
4. Click ... menu → Install from VSIX
5. Select the downloaded file
6. Restart VS Code
```

---

## Option 3: VS Code Marketplace

### Publish to Public Marketplace

#### Prerequisites

1. **Microsoft Account**: Create at https://login.live.com
2. **Azure DevOps Organization**: Create at https://dev.azure.com
3. **Personal Access Token (PAT)**: Generate in Azure DevOps

#### Step 1: Create Publisher

```bash
vsce create-publisher your-publisher-name
```

**Follow prompts**:
- Publisher name (unique identifier)
- Display name (shown in marketplace)
- Email address

#### Step 2: Login

```bash
vsce login your-publisher-name
```

Enter your Personal Access Token when prompted.

#### Step 3: Update package.json

Add publisher field:
```json
{
  "name": "reposense",
  "publisher": "your-publisher-name",
  "version": "0.0.1"
}
```

#### Step 4: Publish

```bash
vsce publish
```

**Output**:
```
Publishing your-publisher-name.reposense@0.0.1...
Successfully published your-publisher-name.reposense@0.0.1!
```

#### Step 5: Verify

1. Go to https://marketplace.visualstudio.com
2. Search for "reposense"
3. Your extension should appear

### Marketplace Requirements

**Must Have**:
- ✅ README.md with description
- ✅ LICENSE file
- ✅ Icon (128x128 or larger)
- ✅ Repository URL
- ✅ Categories
- ✅ Keywords

**Recommended**:
- Screenshots
- GIF demos
- Detailed documentation
- CHANGELOG.md
- Contributing guidelines

### Update Published Extension

```bash
# Increment version in package.json
# Then publish
vsce publish patch  # 0.0.1 → 0.0.2
vsce publish minor  # 0.0.1 → 0.1.0
vsce publish major  # 0.0.1 → 1.0.0
```

---

## Option 4: Private Registry

### For Enterprise/Team Distribution

#### Using Open VSX Registry

1. Create account at https://open-vsx.org
2. Generate access token
3. Publish:
   ```bash
   npx ovsx publish -p YOUR_ACCESS_TOKEN
   ```

#### Using Private NPM Registry

1. Package as npm module
2. Publish to private registry
3. Users install via npm

---

## Pre-Deployment Checklist

### Code Quality

- [ ] All TypeScript compiles without errors
- [ ] No console.log statements in production code
- [ ] Error handling implemented
- [ ] Code commented appropriately
- [ ] No hardcoded credentials or secrets

### Documentation

- [ ] README.md complete and accurate
- [ ] API documentation included
- [ ] Usage examples provided
- [ ] Known issues documented
- [ ] Installation instructions clear

### Testing

- [ ] Extension activates correctly
- [ ] All features work as expected
- [ ] Error cases handled gracefully
- [ ] No memory leaks
- [ ] Performance acceptable

### Legal

- [ ] LICENSE file included
- [ ] Third-party licenses acknowledged
- [ ] No copyright violations
- [ ] Privacy policy (if collecting data)

### Metadata

- [ ] Version number correct
- [ ] Publisher name set
- [ ] Categories appropriate
- [ ] Keywords relevant
- [ ] Icon included and displays correctly

---

## Version Management

### Semantic Versioning

Follow semver: `MAJOR.MINOR.PATCH`

**Examples**:
- `0.0.1` → Initial development
- `0.1.0` → First feature complete
- `1.0.0` → Production ready
- `1.0.1` → Bug fix
- `1.1.0` → New feature
- `2.0.0` → Breaking change

### CHANGELOG.md

Create and maintain:

```markdown
# Changelog

## [0.0.1] - 2026-05-16

### Added
- Initial release
- Workspace analysis feature
- Real-time progress updates
- Health score display
- Backend API integration

### Known Issues
- Backend must be running on localhost:8000
- No configuration options yet
```

### Git Tags

Tag releases:
```bash
git tag -a v0.0.1 -m "Initial release"
git push origin v0.0.1
```

---

## Continuous Deployment

### GitHub Actions Workflow

Create `.github/workflows/publish.yml`:

```yaml
name: Publish Extension

on:
  push:
    tags:
      - 'v*'

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '16'
      
      - name: Install dependencies
        run: npm install
      
      - name: Compile
        run: npm run compile
      
      - name: Package
        run: npx vsce package
      
      - name: Publish
        run: npx vsce publish -p ${{ secrets.VSCE_TOKEN }}
```

### Setup Secrets

1. Go to GitHub repository settings
2. Add secret: `VSCE_TOKEN`
3. Value: Your Personal Access Token

### Trigger Deployment

```bash
git tag v0.0.2
git push origin v0.0.2
# GitHub Actions automatically publishes
```

---

## Rollback Strategy

### If Issues Found After Publishing

#### Option 1: Unpublish (Not Recommended)

```bash
vsce unpublish your-publisher-name.reposense
```

**Warning**: Affects all users immediately

#### Option 2: Publish Fixed Version

```bash
# Fix the issue
# Increment version
vsce publish patch
```

**Better**: Users update at their pace

#### Option 3: Deprecate Version

In marketplace, mark version as deprecated with message pointing to fixed version.

---

## Monitoring After Deployment

### Metrics to Track

1. **Install Count**: How many users installed
2. **Active Users**: Daily/weekly active users
3. **Ratings**: User satisfaction
4. **Reviews**: User feedback
5. **Issues**: Bug reports

### Where to Monitor

- **VS Code Marketplace**: Install stats, ratings
- **GitHub Issues**: Bug reports, feature requests
- **Analytics**: If implemented in extension

### Responding to Feedback

1. **Acknowledge**: Respond to reviews and issues
2. **Prioritize**: Critical bugs first
3. **Communicate**: Update users on fixes
4. **Release**: Push updates regularly

---

## Update Strategy

### Release Cycle

**Recommended**:
- **Patch releases**: As needed for bugs (0.0.x)
- **Minor releases**: Monthly for features (0.x.0)
- **Major releases**: Quarterly for breaking changes (x.0.0)

### Update Notifications

Users see updates in VS Code:
```
Extension Update Available
RepoSense 0.0.1 → 0.0.2
[Update] [Release Notes]
```

### Breaking Changes

If making breaking changes:
1. Increment major version
2. Document in CHANGELOG
3. Provide migration guide
4. Consider deprecation period

---

## Security Considerations

### Before Publishing

- [ ] No API keys in code
- [ ] No passwords in code
- [ ] No sensitive data logged
- [ ] Dependencies up to date
- [ ] Known vulnerabilities patched

### Dependency Audit

```bash
npm audit
npm audit fix
```

### Regular Updates

```bash
# Check for outdated packages
npm outdated

# Update dependencies
npm update
```

---

## Support Plan

### Documentation

- README.md (basic usage)
- Wiki (detailed guides)
- FAQ (common questions)
- API docs (for developers)

### Communication Channels

- GitHub Issues (bug reports)
- GitHub Discussions (questions)
- Email (direct support)
- Discord/Slack (community)

### Response Times

- **Critical bugs**: 24 hours
- **Regular bugs**: 1 week
- **Feature requests**: 1 month
- **Questions**: 48 hours

---

## Deployment Commands Reference

```bash
# Install vsce
npm install -g @vscode/vsce

# Create package
vsce package

# Install locally
code --install-extension reposense-0.0.1.vsix

# Login to marketplace
vsce login your-publisher-name

# Publish
vsce publish

# Publish with version bump
vsce publish patch
vsce publish minor
vsce publish major

# Unpublish (use carefully)
vsce unpublish your-publisher-name.reposense
```

---

## Post-Deployment Checklist

- [ ] Extension appears in marketplace
- [ ] Install works correctly
- [ ] All features functional
- [ ] Documentation accessible
- [ ] Support channels active
- [ ] Monitoring in place
- [ ] Team notified
- [ ] Announcement made

---

**Deployment Status**: ✅ Ready for packaging and distribution