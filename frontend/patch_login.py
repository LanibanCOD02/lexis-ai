import re
with open('src/routes/Login.jsx', 'r') as f:
    content = f.read()

def login_patch(match):
    return """const handleLogin = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err) {
      setErrorMsg(err.message || 'Invalid email or password');
    }
  };"""

content = re.sub(r"const handleLogin = async.*?};\n", login_patch, content, flags=re.DOTALL)

with open('src/routes/Login.jsx', 'w') as f:
    f.write(content)
