import os

files_to_update = [
    'vscode-extension/webview/index.html',
    'vscode-extension/webview/test-dependency-tree.html',
    'vscode-extension/webview/test-complex-tree.html'
]

old_scripts = """    <script src="scripts/utils/formatters.js"></script>
    <script src="scripts/utils/messageHandler.js"></script>
    <script src="scripts/components/Navigation.js"></script>
    <script src="scripts/components/ScoreCard.js"></script>
    <script src="scripts/components/ReviewPanel.js"></script>
    <script src="scripts/components/DocsPanel.js"></script>
    <script src="scripts/components/SecurityPanel.js"></script>
    <script src="scripts/components/ArchitectureGraph.js"></script>
    <script src="scripts/main.js"></script>"""

new_scripts = """    <script src="scripts/main.js"></script>
    <script src="scripts/utils/formatters.js"></script>
    <script src="scripts/utils/messageHandler.js"></script>
    <script src="scripts/components/Navigation.js"></script>
    <script src="scripts/components/ScoreCard.js"></script>
    <script src="scripts/components/ReviewPanel.js"></script>
    <script src="scripts/components/DocsPanel.js"></script>
    <script src="scripts/components/SecurityPanel.js"></script>
    <script src="scripts/components/ArchitectureGraph.js"></script>"""

for filepath in files_to_update:
    with open(filepath, 'r') as f:
        html = f.read()
    
    html = html.replace(old_scripts, new_scripts)
    
    with open(filepath, 'w') as f:
        f.write(html)

print("Order fixed.")
