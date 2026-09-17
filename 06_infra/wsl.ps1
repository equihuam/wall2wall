# Dispatch Python to the separate WSL checkout; configuration remains local.
[CmdletBinding()]
param([Parameter(Mandatory=$true)][string[]]$PythonArgs)
$ErrorActionPreference = 'Stop'
$repo = Split-Path $PSScriptRoot -Parent
$config = Get-Content -LiteralPath (Join-Path $repo 'local_state/wsl-tools.json') -Raw | ConvertFrom-Json
if (-not $config.distribution -or -not $config.checkout) { throw 'Missing WSL distribution or checkout.' }
& wsl.exe --distribution $config.distribution --cd $config.checkout --exec bash 06_infra/linux.sh @PythonArgs
exit $LASTEXITCODE
