$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [Console]::OutputEncoding

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$taskRoot = Split-Path -Parent $scriptDir
$repoRoot = Split-Path -Parent $taskRoot
$generator = Join-Path $scriptDir "rebuild_task_board.py"
$promptFile = Join-Path $taskRoot "outputs\\next_prompt.txt"

python $generator | Out-Null

if (-not (Test-Path $promptFile)) {
    throw "Prompt file was not generated: $promptFile"
}

Get-Content -Raw $promptFile -Encoding UTF8
