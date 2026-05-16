with open('vscode-extension/webview/main.html', 'r') as f:
    html = f.read()

# Fix CSS
html = html.replace('href="styles/main.css"', 'href="styles.css"')

# Remove all script tags that were added
scripts = [
    '<script src="scripts/utils/formatters.js"></script>',
    '<script src="scripts/utils/messageHandler.js"></script>',
    '<script src="scripts/components/Navigation.js"></script>',
    '<script src="scripts/components/ScoreCard.js"></script>',
    '<script src="scripts/components/ReviewPanel.js"></script>',
    '<script src="scripts/components/DocsPanel.js"></script>',
    '<script src="scripts/components/SecurityPanel.js"></script>',
    '<script src="scripts/components/ArchitectureGraph.js"></script>',
    '<script src="scripts/main.js"></script>'
]

for s in scripts:
    html = html.replace(s, '')
    
# Add single main.js back
html = html.replace('</body>', '    <script src="main.js"></script>\n</body>')

with open('vscode-extension/webview/main.html', 'w') as f:
    f.write(html)
