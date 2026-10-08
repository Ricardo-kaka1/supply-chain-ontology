param([ValidateSet('doctor','qc','build','demo','test','native-test','protege')][string]$Action='doctor')
$ErrorActionPreference='Stop'
$repo=Split-Path $PSScriptRoot -Parent
$lock=Get-Content -LiteralPath (Join-Path $repo 'config/toolchain.lock.json') -Raw | ConvertFrom-Json
$env:PYTHONPATH=Join-Path $repo 'src'
$env:PYSTOW_HOME=Join-Path $repo 'build/cache'
$env:PYTHONUTF8='1'
if ($Action -eq 'native-test') {
    & (Join-Path $repo '.venv/Scripts/python.exe') (Join-Path $repo 'scripts/native_check.py')
    exit $LASTEXITCODE
}
if ($Action -eq 'protege') {
    $app=Join-Path $repo '.tools/Protege-5.6.9/run.bat'
    if (-not (Test-Path -LiteralPath $app)) { throw 'Download the pinned portable Protege package; see docs/manual.zh.md' }
    Start-Process -FilePath $app -ArgumentList ('"'+(Join-Path $repo 'src/ontology/scaudit-edit.owl')+'"') -WorkingDirectory (Split-Path $app) -WindowStyle Hidden
    Write-Output 'Protege launch requested. Confirm imports, bilingual labels and individuals using docs/manual.zh.md.'
    exit 0
}
$docker=Get-Command docker -ErrorAction SilentlyContinue
if (-not $docker) { throw 'Docker is unavailable. Install/enable WSL2 and Docker Desktop with your administrator. Native tests remain available: scripts/cabot.ps1 native-test' }
$engine=& docker info --format '{{.OSType}}'
if ($LASTEXITCODE -ne 0 -or $engine -ne 'linux') { throw 'Docker Linux engine is not ready.' }
$base=@('run','--rm','--platform',$lock.platform,'--mount',"type=bind,source=$repo,target=/work",'-w','/work/src/ontology','-e','PYSTOW_HOME=/work/build/cache',$lock.odk_image)
if ($Action -eq 'doctor') {
    & docker @base python /work/scripts/tool_versions.py
} else {
    & docker @base make "sca-$Action" IMP=false
}
if ($LASTEXITCODE -ne 0) { throw "Docker $Action failed with exit $LASTEXITCODE" }
