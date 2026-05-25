Get-Process mongod -ErrorAction SilentlyContinue | ForEach-Object {
    Write-Host "🛑 Arrêt de mongod PID $($_.Id)"
    Stop-Process -Id $_.Id -Force
}
