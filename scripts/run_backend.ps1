param(
    [string]$ApiHost = "127.0.0.1",
    [int]$Port = 8000
)

Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Path)\..
Set-Location -Path .\backend
$env:PYTHONPATH = (Get-Location).Path
python -m uvicorn src.api.main:app --host $ApiHost --port $Port --reload

