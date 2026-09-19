# Native M008 adapter. Explicit local configuration; no global environment changes.
[CmdletBinding()]
param([string]$Config, [ValidateSet('suite','echo','nonzero')][string]$Mode='suite', [string]$Payload='')
$ErrorActionPreference = 'Stop'
function Invoke-M008Native {
    param([string]$ConfigPath, [string]$ProbeMode='suite', [string]$ProbePayload='')
    if ($ProbeMode -notin @('suite','echo','nonzero')) { throw 'Unknown mode' }
    $settings = Get-Content -LiteralPath $ConfigPath -Raw -Encoding UTF8 | ConvertFrom-Json
    foreach ($tool in @($settings.conda,$settings.bash,(Join-Path $settings.prefix 'python.exe'))) {
        if (-not (Test-Path -LiteralPath $tool -PathType Leaf)) { throw 'Missing configured executable' }
    }
    if ($settings.bash -match '(?i)WindowsApps|Windows[\\/]System32') { throw 'Native Git Bash required' }
    $gitRoot = Split-Path (Split-Path $settings.bash -Parent) -Parent
    $values = @{
        PATH = (@((Join-Path $gitRoot 'cmd'),(Join-Path $gitRoot 'bin'),(Join-Path $env:SystemRoot 'System32'),$env:SystemRoot) -join ';')
        WALL2WALL_BASH=$settings.bash; PYTHONUTF8='1'; PYTHONNOUSERSITE='1'; PYTHONDONTWRITEBYTECODE='1'
        PYTHONPATH=$null; PYTHONHOME=$null; GDAL_DATA=$null; PROJ_LIB=$null; PROJ_DATA=$null
        BASH_ENV=$null; ENV=$null; MSYS2_ARG_CONV_EXCL=$null; MSYS2_ENV_CONV_EXCL=$null
        OMP_NUM_THREADS='1'; OPENBLAS_NUM_THREADS='1'; MKL_NUM_THREADS='1'
        PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'; VERIFICATION_SCRATCH=$settings.scratch
        TMP=$settings.scratch; TEMP=$settings.scratch; TMPDIR=$settings.scratch
    }
    $saved=@{}
    try {
        foreach ($key in $values.Keys) {
            $saved[$key]=[Environment]::GetEnvironmentVariable($key,'Process')
            [Environment]::SetEnvironmentVariable($key,$values[$key],'Process')
        }
        $worker=Join-Path $settings.snapshot '06_infra/m008_native/worker.py'
        $arguments=@('run','--no-capture-output','--prefix',$settings.prefix,'python','-B',$worker,'--config',$ConfigPath)
        if ($ProbeMode -ne 'suite') { $arguments+=@('--probe',$ProbeMode,'--payload',$ProbePayload) }
        & $settings.conda @arguments
        $script:M008Exit=$LASTEXITCODE
    } finally {
        foreach ($key in $saved.Keys) { [Environment]::SetEnvironmentVariable($key,$saved[$key],'Process') }
    }
}
if ($MyInvocation.InvocationName -ne '.') {
    Invoke-M008Native -ConfigPath $Config -ProbeMode $Mode -ProbePayload $Payload
    exit $script:M008Exit
}
