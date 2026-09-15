# Run Python in the fixed Windows environment without changing the caller's PATH.
[CmdletBinding()]
param([Parameter(Mandatory=$true)][string[]]$PythonArgs)
$ErrorActionPreference = 'Stop'
$repo = Split-Path $PSScriptRoot -Parent
$config = Get-Content -LiteralPath (Join-Path $repo 'local_state/windows-tools.json') -Raw | ConvertFrom-Json
$prefix = Join-Path $repo 'local_state/envs/wall2wall-win'
foreach ($executable in @($config.conda, $config.bash, (Join-Path $prefix 'python.exe'))) {
    if (-not (Test-Path -LiteralPath $executable -PathType Leaf)) { throw "Missing executable: $executable" }
}
if ($config.bash -match '(?i)WindowsApps|Windows[\\/]System32') { throw 'Select native Git Bash, not WSL.' }
$gitRoot = Split-Path (Split-Path $config.bash -Parent) -Parent
$values = @{
    PATH = (@((Join-Path $gitRoot 'cmd'), (Join-Path $gitRoot 'bin'),
        (Join-Path $env:SystemRoot 'System32'), $env:SystemRoot) -join ';')
    WALL2WALL_BASH = $config.bash
    PYTHONUTF8 = '1'
    PYTHONNOUSERSITE = '1'
    PYTHONDONTWRITEBYTECODE = '1'
    PYTHONPATH = $null
    PYTHONHOME = $null
    GDAL_DATA = $null
    PROJ_LIB = $null
    PROJ_DATA = $null
    BASH_ENV = $null
    ENV = $null
    MSYS2_ARG_CONV_EXCL = $null
    MSYS2_ENV_CONV_EXCL = $null
    OMP_NUM_THREADS = '1'
    OPENBLAS_NUM_THREADS = '1'
    MKL_NUM_THREADS = '1'
}
$saved = @{}
try {
    foreach ($key in $values.Keys) {
        $saved[$key] = [Environment]::GetEnvironmentVariable($key, 'Process')
        [Environment]::SetEnvironmentVariable($key, $values[$key], 'Process')
    }
    & $config.conda run --no-capture-output --prefix $prefix python @PythonArgs
    $result = $LASTEXITCODE
} finally {
    foreach ($key in $saved.Keys) {
        [Environment]::SetEnvironmentVariable($key, $saved[$key], 'Process')
    }
}
exit $result
