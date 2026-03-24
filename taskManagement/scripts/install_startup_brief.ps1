$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$startupDir = [Environment]::GetFolderPath("Startup")
$launcherPath = Join-Path $startupDir "duty-task-brief.cmd"
$briefScript = Join-Path $scriptDir "show_startup_brief.ps1"

$content = "@echo off`r`nchcp 65001 >nul`r`npowershell -ExecutionPolicy Bypass -File `"$briefScript`"`r`npause`r`n"
Set-Content -Path $launcherPath -Value $content -Encoding ASCII

Write-Output "Installed startup launcher: $launcherPath"
