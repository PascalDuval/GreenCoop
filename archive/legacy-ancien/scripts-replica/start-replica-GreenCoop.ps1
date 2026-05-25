# ================================================
# PowerShell Script - Start MongoDB Replica Set
# ================================================

Write-Host "Démarrage du Replica Set rsGreenCoop..." -ForegroundColor Cyan

$mongod   = "C:\Program Files\MongoDB\Server\8.0\bin\mongod.exe"
$basePath = "C:\Users\karap\mongodb"

$nodes = @(
    @{ name = "PRIMARY";         port = 27017; folder = "rs-primary" }
    @{ name = "ANALYSTE";        port = 27018; folder = "rs-analyste" }
    @{ name = "SECONDARY_CLONE"; port = 27019; folder = "rs-clone" }
)

# Création des dossiers
foreach ($node in $nodes) {
    $dataPath = Join-Path $basePath $node.folder
    if (-not (Test-Path $dataPath)) {
        New-Item -ItemType Directory -Path $dataPath | Out-Null
    }
}

# Démarrage des noeuds
foreach ($node in $nodes) {
    $dataPath = Join-Path $basePath $node.folder
    $logPath  = Join-Path $dataPath "mongod.log"

    Write-Host "Démarrage $($node.name) sur le port $($node.port)..."

    $args = "--port $($node.port) --dbpath `"$dataPath`" --replSet rsGreenCoop --bind_ip localhost --logpath `"$logPath`" --logappend"

    Start-Process -FilePath $mongod -ArgumentList $args -WindowStyle Normal
}

Write-Host "Replica Set rsGreenCoop lancé avec succès." -ForegroundColor Green
