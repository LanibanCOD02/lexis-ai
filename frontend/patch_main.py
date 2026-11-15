import os
with open('src/main.jsx', 'r') as f:
    content = f.read()
import_axios = 'import axios from "axios";\naxios.defaults.baseURL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";\n'
content = content.replace("import App from './App.jsx'", "import App from './App.jsx'\n" + import_axios)
with open('src/main.jsx', 'w') as f:
    f.write(content)
