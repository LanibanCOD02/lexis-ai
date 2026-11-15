import re
with open('src/routes/Register.jsx', 'r') as f:
    content = f.read()

def register_error_patch(match):
    return """} catch (err) {
      setErrorMsg(err.message || 'Registration failed');
    }"""

content = re.sub(r"\} catch \(err\) \{\n\s*setErrorMsg\(err\.response\?\.data\?\.detail \|\| 'Registration failed'\);\n\s*\}", register_error_patch, content)

with open('src/routes/Register.jsx', 'w') as f:
    f.write(content)
