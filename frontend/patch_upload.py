import re
with open('src/components/DocumentUpload.jsx', 'r') as f:
    content = f.read()

# Replace the handleFileUpload logic
def handle_upload_patch(match):
    return """const handleFileUpload = async (selectedFile) => {
    if (!selectedFile) return;
    setFile(selectedFile);
    setStatus('error');
    setErrorMsg('Document ingestion is currently disabled. Please use the core research engine with the pre-loaded corpus.');
  };"""

content = re.sub(r"const handleFileUpload = async.*?setStatus\('success'\);\n\s*if \(onUploadComplete\) onUploadComplete\(res\.data\);\n\s*\} catch \(err\) \{.*?\n\s*\}\n\s*\};", handle_upload_patch, content, flags=re.DOTALL)

with open('src/components/DocumentUpload.jsx', 'w') as f:
    f.write(content)
