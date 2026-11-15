import re
with open('src/context/AuthContext.jsx', 'r') as f:
    content = f.read()

def auth_patch(match):
    return """const login = async (email, password) => {
    setLoading(true);
    try {
      // Backend does not enforce auth currently, bypass login for testing
      setToken("dummy_token");
      setUser({ email: email, role: 'Lawyer' });
      return true;
    } catch (err) {
      console.error(err);
      return false;
    } finally {
      setLoading(false);
    }
  };"""

content = re.sub(r"const login = async.*?finally \{\n\s*setLoading\(false\);\n\s*\}\n\s*\};", auth_patch, content, flags=re.DOTALL)

with open('src/context/AuthContext.jsx', 'w') as f:
    f.write(content)
