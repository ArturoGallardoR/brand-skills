param(
    [Parameter(Position = 0, Mandatory = $true)]
    [string]$Name,

    [Parameter(Position = 1, ValueFromRemainingArguments = $true)]
    [string[]]$Platforms
)

$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonScript = Join-Path $scriptDir 'check_availability.py'
$argsList = @($pythonScript, $Name) + $Platforms

if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 @argsList
    exit $LASTEXITCODE
}
if (Get-Command python -ErrorAction SilentlyContinue) {
    & python @argsList
    exit $LASTEXITCODE
}

Write-Error 'Python 3 was not found. Install Python 3 or add py/python to PATH.'
exit 1
