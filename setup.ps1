$ErrorActionPreference = 'Stop'
if (-not (Test-Path '.venv')) { py -m venv .venv }
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
& .\.venv\Scripts\python.exe manage.py migrate
& .\.venv\Scripts\python.exe manage.py seed_biblioteca
& .\.venv\Scripts\python.exe manage.py seed_market
Write-Host 'Listo. Ejecuta: .\.venv\Scripts\python.exe manage.py runserver' -ForegroundColor Green
