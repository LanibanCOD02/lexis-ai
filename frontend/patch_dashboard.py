import re

with open('src/routes/Dashboard.jsx', 'r') as f:
    content = f.read()

# Remove the /api/v1/cases/ fetch
fetch_pattern = re.compile(r"useEffect\(\(\) => \{\s*axios\.get\('/api/v1/cases/'\).*?\}\s*\}\]\);\s*", re.DOTALL)
content = fetch_pattern.sub('', content)

with open('src/routes/Dashboard.jsx', 'w') as f:
    f.write(content)
