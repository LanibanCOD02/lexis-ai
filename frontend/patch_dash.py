import re
with open('src/routes/Dashboard.jsx', 'r') as f:
    content = f.read()

def dash_patch(match):
    return """useEffect(() => {
    // Legacy cases API removed; dashboard degraded gracefully.
  }, []);"""

content = re.sub(r"useEffect\(\(\) => \{\n\s*axios\.get\('/api/v1/cases/'\).*?\}\, \[\]\);", dash_patch, content, flags=re.DOTALL)

with open('src/routes/Dashboard.jsx', 'w') as f:
    f.write(content)
