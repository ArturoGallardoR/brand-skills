param()

$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonScript = Join-Path $scriptDir 'validate_skills.py'

if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 $pythonScript
    exit $LASTEXITCODE
}
if (Get-Command python -ErrorAction SilentlyContinue) {
    & python $pythonScript
    exit $LASTEXITCODE
}

Write-Error 'Python 3 was not found. Install Python 3 or add py/python to PATH.'
exit 1
