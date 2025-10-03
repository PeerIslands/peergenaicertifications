Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Path)\..
Set-Location -Path .\backend

python -m pip install -U pip
pip install -r requirements.txt

$env:PYTHONPATH = (Get-Location).Path
python -c "import src.validation.validator as v; raise SystemExit(v.run_validation())"


