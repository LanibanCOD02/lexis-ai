import re
with open('src/context/AuthContext.jsx', 'r') as f:
    content = f.read()

def register_patch(match):
    return """const register = async (email, password) => {
    setLoading(true);
    try {
      // Backend does not enforce auth currently, bypass register for testing
      setToken("dummy_token");
      setUser({ email: email, role: 'Lawyer' });
      return true;
    } catch (error) {
      console.error("Registration failed:", error);
      throw error;
    } finally {
      setLoading(false);
    }
  };"""

content = re.sub(r"const register = async.*?finally \{\n\s*setLoading\(false\);\n\s*\}\n\s*\};", register_patch, content, flags=re.DOTALL)

with open('src/context/AuthContext.jsx', 'w') as f:
    f.write(content)
