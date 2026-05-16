import glob
import re

new_csp = "default-src 'none'; style-src 'unsafe-inline' https://cdn.jsdelivr.net http: https: vscode-webview-resource:; script-src 'unsafe-inline' https://cdn.jsdelivr.net http: https: vscode-webview-resource:; img-src https: data: http: vscode-webview-resource:; connect-src ws: wss: http: https:;"

for filepath in glob.glob('vscode-extension/webview/*.html'):
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Replace any existing CSP meta tag with the new relaxed one
    content = re.sub(r'<meta http-equiv="Content-Security-Policy"\s+content="[^"]+">', 
                     f'<meta http-equiv="Content-Security-Policy" content="{new_csp}">', 
                     content)
                     
    with open(filepath, 'w') as f:
        f.write(content)

print("CSP updated in all HTML files.")
