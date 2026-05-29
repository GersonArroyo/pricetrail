$ErrorActionPreference = "Stop"

$TaskName = "PriceTrailScraper"
$ProjectDir = Resolve-Path (Join-Path $PSScriptRoot "..")
$LogDir = Join-Path $ProjectDir "logs"
$LogFile = Join-Path $LogDir "scraper.log"
$ScraperPath = Join-Path $ProjectDir "scraper\scraper.py"

if (!(Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir | Out-Null
}

$PythonCommand = "python"
$TaskAction = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -Command `"Set-Location '$ProjectDir'; docker compose run --rm pricetrail python -c 'from scraper.scraper import run; run()' >> '$LogFile' 2>&1`""

$TaskTrigger = New-ScheduledTaskTrigger -Daily -At 2:00AM
$TaskPrincipal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel LeastPrivilege

if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $TaskAction `
    -Trigger $TaskTrigger `
    -Principal $TaskPrincipal `
    -Description "Runs the PriceTrail scraper every day at 2 AM."

Write-Host "Scheduled task installed:"
Write-Host "Name: $TaskName"
Write-Host "Schedule: every day at 02:00"
Write-Host "Project: $ProjectDir"
Write-Host "Log: $LogFile"
