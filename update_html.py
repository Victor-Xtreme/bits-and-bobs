import os
import re

files_to_update = [
    'vscode-extension/webview/index.html',
    'vscode-extension/webview/test-dependency-tree.html',
    'vscode-extension/webview/test-complex-tree.html'
]

scripts_to_inject = """
    <script src="scripts/utils/formatters.js"></script>
    <script src="scripts/utils/messageHandler.js"></script>
    <script src="scripts/components/Navigation.js"></script>
    <script src="scripts/components/ScoreCard.js"></script>
    <script src="scripts/components/ReviewPanel.js"></script>
    <script src="scripts/components/DocsPanel.js"></script>
    <script src="scripts/components/SecurityPanel.js"></script>
    <script src="scripts/components/ArchitectureGraph.js"></script>
    <script src="scripts/main.js"></script>
"""

for filepath in files_to_update:
    with open(filepath, 'r') as f:
        html = f.read()
    
    # Update CSS link
    html = html.replace('href="styles.css"', 'href="styles/main.css"')
    
    # Remove old main.js if exists
    html = html.replace('<script src="main.js"></script>', '')
    
    # Fix sample data path in test files
    html = html.replace('src="sample-data.js"', 'src="scripts/sample-data.js"')
    html = html.replace('src="sample-data-complex.js"', 'src="scripts/sample-data-complex.js"')
    
    # Inject new scripts before </body> or inside <head> depending on where they were.
    # In main.html they were not included (they were injected by extension probably? Let's check index.html)
    if '</body>' in html:
        # If there are already script tags right before body, replace them.
        # Actually just put them before </body>
        html = html.replace('</body>', scripts_to_inject + '\n</body>')
    
    with open(filepath, 'w') as f:
        f.write(html)

print("HTML files updated.")
