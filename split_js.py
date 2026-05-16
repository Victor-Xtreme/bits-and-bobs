import re

with open('webview/main.js', 'r') as f:
    js = f.read()

def extract_funcs(names, content):
    extracted = []
    # match function name(...) { ... }
    for name in names:
        pattern = r"(?:async\s+)?function\s+" + name + r"\s*\([\s\S]*?^}"
        matches = re.finditer(pattern, content, re.MULTILINE)
        for match in matches:
            extracted.append(match.group(0))
            # replace with empty string
            content = content.replace(match.group(0), '')
    return "\n\n".join(extracted), content

def extract_block(start_str, end_str, content):
    start_idx = content.find(start_str)
    if start_idx == -1: return "", content
    end_idx = content.find(end_str, start_idx)
    if end_idx == -1: end_idx = len(content)
    else: end_idx += len(end_str)
    block = content[start_idx:end_idx]
    return block, content[:start_idx] + content[end_idx:]

# Specific files
components = {}

# formatters.js
comp, js = extract_funcs(['escapeHtml', 'copyToClipboard'], js)
comp += "\nwindow.copyToClipboard = copyToClipboard;"
js = js.replace("window.copyToClipboard = copyToClipboard;", "")
components['vscode-extension/webview/scripts/utils/formatters.js'] = comp

# ScoreCard.js
comp, js = extract_funcs(['renderHealthPanel', 'animateScore'], js)
components['vscode-extension/webview/scripts/components/ScoreCard.js'] = comp

# ReviewPanel.js
comp, js = extract_funcs(['renderReviewPanel'], js)
components['vscode-extension/webview/scripts/components/ReviewPanel.js'] = comp

# DocsPanel.js
comp, js = extract_funcs(['renderDocsPanel'], js)
components['vscode-extension/webview/scripts/components/DocsPanel.js'] = comp

# SecurityPanel.js
comp, js = extract_funcs(['renderSecurityPanel'], js)
components['vscode-extension/webview/scripts/components/SecurityPanel.js'] = comp

# messageHandler.js
comp, js = extract_funcs(['showLoadingState', 'updateProgress', 'showError', 'showResults', 'hideAllStates', 'updateBadges'], js)
components['vscode-extension/webview/scripts/utils/messageHandler.js'] = comp

# Navigation.js
comp, js = extract_funcs(['switchPanel'], js)
components['vscode-extension/webview/scripts/components/Navigation.js'] = comp

# ArchitectureGraph.js
# This one also has let currentSelectedNode... before renderArchitecturePanel
arch_vars = """let currentSelectedNode = null;
let currentDepth = 1;
let currentGraphView = 'tree'; // 'network' or 'tree'
let graphSimulation = null;"""
js = js.replace(arch_vars, "")

comp, js = extract_funcs(['renderArchitecturePanel', 'buildSubgraph', 'renderDependencyTree', 'zoomGraph', 'resetGraphZoom', 'renderNetworkGraph'], js)
components['vscode-extension/webview/scripts/components/ArchitectureGraph.js'] = arch_vars + "\n\n" + comp

# The rest goes to main.js
components['vscode-extension/webview/scripts/main.js'] = js.strip()

for filepath, content in components.items():
    with open(filepath, 'w') as f:
        f.write(content.strip() + "\n")

print("Files split successfully.")
