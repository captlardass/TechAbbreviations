<#
.SYNOPSIS
    Adds techabbr.py to your PATH as `abbr` (Windows).
#>

param(
    [string]$TargetDir = "$HOME\bin"
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$TechAbbrPath = Join-Path $ScriptDir "techabbr.py"

New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null

$WrapperPath = Join-Path $TargetDir "abbr.cmd"
$WrapperContent = @"
@echo off
where python >nul 2>nul
if %ERRORLEVEL%==0 (
    python "$TechAbbrPath" %*
) else (
    py "$TechAbbrPath" %*
)
"@
Set-Content -Path $WrapperPath -Value $WrapperContent -Encoding ASCII

Write-Host "Created $WrapperPath -> $TechAbbrPath"

$UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
if (($UserPath -split ";") -notcontains $TargetDir) {
    Write-Host "$TargetDir is not on your PATH."
    Write-Host "Add it for future sessions with:"
    Write-Host "  [Environment]::SetEnvironmentVariable('Path', `"`$env:Path;$TargetDir`", 'User')"
    Write-Host "Then restart your terminal."
} else {
    Write-Host "Run 'abbr --help' to get started."
}
