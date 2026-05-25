Write-Host "============================================="
Write-Host " REPLICA SET STARTUP - GreenCoop"
Write-Host "============================================="

# ---------- CONFIG ----------
$MONGOSH = $env:MONGOSH_PATH
if (-not $MONGOSH) {
    $MONGOSH = "C:\Users\karap\Downloads\mongosh-2.5.10-win32-x64\mongosh-2.5.10-win32-x64\bin\mongosh.exe"
}

$PRIMARY_PORT = 27027
$SECONDARY1_PORT = 27028
$SECONDARY2_PORT = 27029

$InitScript = Join-Path $PSScriptRoot "scripts-replica\init-replica-GreenCoop.js"
$CreateUsersScript = Join-Path $PSScriptRoot "scripts-replica\create-users.js"

# ---------- 0. Check Docker ----------
Write-Host "Checking Docker Desktop..."
try {
    docker info | Out-Null
} catch {
    Write-Host "ERROR: Docker Desktop is not running."
    exit 1
}

# ---------- 1. Clean and start ----------
Write-Host "Stopping and removing containers..."
docker compose down -v

Write-Host "Starting containers..."
docker compose up -d --build

Write-Host "Waiting for MongoDB (30s)..."
Start-Sleep -Seconds 30

# ---------- 2. Init replica set ----------
Write-Host "Initializing replica set..."
& $MONGOSH --host "localhost:$PRIMARY_PORT" $InitScript

Write-Host "Waiting for PRIMARY election (20s)..."
Start-Sleep -Seconds 20

# ---------- 3. Replica status ----------
Write-Host "Replica set status:"
& $MONGOSH --host "localhost:$PRIMARY_PORT" --eval "
rs.status().members.forEach(function(m){
  print(m.name + ' : ' + m.stateStr)
})
" admin

# ---------- 4. Users ----------
Write-Host "Creating users (idempotent)..."
& $MONGOSH --host "localhost:$PRIMARY_PORT" $CreateUsersScript

# ---------- 5. Test SECONDARY read ----------
Write-Host "Testing read on SECONDARY (mongo2)..."
& $MONGOSH --host "localhost:$SECONDARY1_PORT" `
  -u analyste `
  -p readonly123 `
  --authenticationDatabase admin `
  GreenCoop `
  --eval "
rs.secondaryOk();
db.ObsProEtAmateur.findOne()
"

# ---------- 6. Run data_migration ----------
Write-Host "Running data_migration container..."
docker start -a data_migration

Write-Host "============================================="
Write-Host " REPLICA SET GreenCoop READY"
Write-Host " PRIMARY   : localhost:$PRIMARY_PORT"
Write-Host " SECONDARY : localhost:$SECONDARY1_PORT / $SECONDARY2_PORT"
Write-Host "============================================="
