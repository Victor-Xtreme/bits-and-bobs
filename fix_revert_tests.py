import os
for f_name in ['vscode-extension/webview/test-complex-tree.html', 'vscode-extension/webview/test-dependency-tree.html']:
    with open(f_name, 'r') as f:
        html = f.read()

    # Fix CSS
    html = html.replace('href="styles/main.css"', 'href="styles.css"')
    
    # Fix sample data
    html = html.replace('src="scripts/sample-data.js"', 'src="sample-data.js"')
    html = html.replace('src="scripts/sample-data-complex.js"', 'src="sample-data-complex.js"')

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

    with open(f_name, 'w') as f:
        f.write(html)
