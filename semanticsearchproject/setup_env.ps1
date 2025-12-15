$ErrorActionPreference = 'Stop'
# Create virtual environment in .venv and install requirements into that venv
if (-Not (Test-Path -Path ".venv")) {
    python -m venv .venv
}
# Use the venv's python executable to install packages so activation isn't required
& .\.venv\Scripts\python -m pip install --upgrade pip
& .\.venv\Scripts\python -m pip install -r requirements.txt
Write-Host "Environment setup complete. To activate the venv in this session: . .\.venv\Scripts\Activate.ps1"
