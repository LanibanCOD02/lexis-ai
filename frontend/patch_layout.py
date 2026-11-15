import re
with open('src/routes/LandingPage.jsx', 'r') as f:
    content = f.read()

def layout_patch(match):
    return """return (
      <div className="min-h-screen bg-background text-foreground font-sans selection:bg-primary selection:text-white bg-paper-texture relative overflow-x-hidden w-full max-w-[100vw]">"""

content = re.sub(r"return \(\n\s*<div className=\"min-h-screen bg-background text-foreground font-sans selection:bg-primary selection:text-white\s+bg-paper-texture relative\">", layout_patch, content)

with open('src/routes/LandingPage.jsx', 'w') as f:
    f.write(content)
