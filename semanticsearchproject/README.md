# semanticsearchproject — Environment setup

This repository contains `collecting.py`. The files added here provide a minimal, repeatable Python environment setup for Windows PowerShell.

Quick steps (PowerShell):

```powershell
cd path\to\semanticsearchproject
# create venv and install dependencies
.\setup_env.ps1
# activate and run
. .\.venv\Scripts\Activate.ps1
python .\collecting.py
```

Notes:
- The `requirements.txt` contains `sentence-transformers` and common libs. `faiss-cpu` can speed up vector search but may be tricky to install on Windows; use conda if you need it.
- If PowerShell blocks script execution, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force` then re-run `.\setup_env.ps1`.

Files added:

- `requirements.txt`: dependency pins
- `pyproject.toml`: minimal project metadata
- `setup_env.ps1`: creates `.venv` and installs requirements
- `run_collecting.ps1`: activate venv and run `collecting.py`
- `.gitignore`: ignores `.venv` and caches
