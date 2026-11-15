$env:LEXIS_DATA_ROOT = "D:\Lexis Backend\LEXIS_AI"
$env:LEXIS_DEVICE = "cpu"
$env:HF_HUB_DISABLE_SYMLINKS_WARNING = "1"

# Load .env file if it exists
$envPath = "D:\Lexis Backend\LEXIS_AI\.env"
if (Test-Path $envPath) {
    foreach ($line in Get-Content $envPath) {
        if ($line -match '^\s*([^#\s]+?)\s*=\s*(.*)$') {
            $name = $matches[1]
            $value = $matches[2].Trim(" `"'")
            Set-Item -Path "Env:$name" -Value $value
        }
    }
}

Write-Host "Starting Lexis AI Backend..."
cd "D:\Lexis Backend\LEXIS_AI\backend"
..\venv_test\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
