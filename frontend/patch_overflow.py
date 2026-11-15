import re
with open('src/index.css', 'r') as f:
    content = f.read()

def root_patch(match):
    return """@layer base {
  html, body {
    overflow-x: hidden;
    width: 100%;
    position: relative;
    max-width: 100vw;
  }
  :root {"""

content = re.sub(r"@layer base \{\n  :root \{", root_patch, content)

with open('src/index.css', 'w') as f:
    f.write(content)
