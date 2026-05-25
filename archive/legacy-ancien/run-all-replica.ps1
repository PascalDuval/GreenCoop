Write-Host "============================================="
Write-Host " DEMARRAGE COMPLET REPLICA SET GreenCoop"
Write-Host "============================================="

# ---------- CONFIG ----------
$MONGOSH = "C:\Users\karap\Downloads\mongosh-2.5.10-win32-x64\mongosh-2.5.10-win32-x64\bin\mongosh.exe"

$PRIMARY_PORT   = 27027
$SECONDARY1_PORT = 27028
$SECONDARY2_PORT = 27029

# ---------- 0. Vérification Docker ----------
Write-Host "Verification Docker Desktop..."
try {
    docker info | Out-Null
} catch {
    Write-Host "ERREUR : Docker Desktop n'est pas lance"
    exit 1
}

# ---------- 1. Nettoyage + démarrage ----------
Write-Host "Arret et nettoyage Docker..."
docker compose down -v

Write-Host "Lancement des conteneurs Docker..."
docker compose up -d --build

Write-Host "Attente demarrage MongoDB (30s)..."
Start-Sleep -Seconds 30

# ---------- 2. Initialisation Replica Set ----------
Write-Host "Initialisation du Replica Set (si non deja fait)..."

& $MONGOSH --host "localhost:$PRIMARY_PORT" --eval "
try {
  rs.status()
  print('Replica Set deja initialise')
} catch (e) {
  rs.initiate({
    _id: 'rsGreenCoop',
    members: [
      { _id: 0, host: 'mongo1:27017', priority: 2 },
      { _id: 1, host: 'mongo2:27017', priority: 1 },
      { _id: 2, host: 'mongo3:27017', priority: 1 }
    ]
  })
  print('Replica Set initialise')
}
" admin

Write-Host "Attente election PRIMARY (20s)..."
Start-Sleep -Seconds 20

# ---------- 3. Etat Replica Set ----------
Write-Host "Etat du Replica Set :"
& $MONGOSH --host "localhost:$PRIMARY_PORT" --eval "
rs.status().members.forEach(function(m){
  print(m.name + ' : ' + m.stateStr)
})
" admin

# ---------- 4. Création utilisateur analyste (idempotent) ----------
Write-Host "Verification utilisateur analyste..."

& $MONGOSH --host "localhost:$PRIMARY_PORT" --eval "
db = db.getSiblingDB('admin')
if (!db.getUser('analyste')) {
  db.createUser({
    user: 'analyste',
    pwd: 'readonly123',
    roles: [{ role: 'read', db: 'GreenCoop' }]
  })
  print('Utilisateur analyste cree')
} else {
  print('Utilisateur analyste existe deja')
}
" admin

# ---------- 5. Test lecture SECONDARY ----------
Write-Host "Test lecture sur SECONDARY (mongo2)..."

& $MONGOSH --host "localhost:$SECONDARY1_PORT" `
  -u analyste `
  -p readonly123 `
  --authenticationDatabase admin `
  GreenCoop `
  --eval "
rs.secondaryOk();
db.ObsProEtAmateur.findOne()
"

# ---------- 6. Execution data_migration ----------
Write-Host "Execution restore_and_visualize.py via container..."

docker start -a data_migration

Write-Host "============================================="
Write-Host " Replica Set GreenCoop OPERATIONNEL"
Write-Host " PRIMARY   : localhost:$PRIMARY_PORT"
Write-Host " SECONDARY : localhost:$SECONDARY1_PORT / $SECONDARY2_PORT"
Write-Host "============================================="
