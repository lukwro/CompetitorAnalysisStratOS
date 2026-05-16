param(
  [switch]$InstallDeps
)

$python = 'C:\Users\lukwro\AppData\Local\Programs\Python\Python312\python.exe'
if (-not (Test-Path -LiteralPath $python)) {
  throw "Python not found at: $python"
}

Set-Location -LiteralPath $PSScriptRoot

if ($InstallDeps) {
  & $python -m pip install -r requirements.txt
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

& $python -m pytest
exit $LASTEXITCODE
