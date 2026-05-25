# ================================
# 📘 Guide de lancement Replica Set GreenCoop
# ================================

## Étape 1 - Démarrer tous les nœuds MongoDB
Depuis PowerShell :
cd C:\Users\karap\OpenClassRooms\dataprojet8\scripts
.\start-replica-GreenCoop.ps1

## Étape 2 - Initialiser le Replica Set + Utilisateur
Toujours dans PowerShell :
#"C:\Program Files\MongoDB\Server\8.0\bin\mongosh.exe" --port 27017 init-replica-GreenCoop.js
 & "C:\Users\karap\Downloads\mongosh-2.5.10-win32-x64\mongosh-2.5.10-win32-x64\bin\mongosh.exe" --port 27017 .\init-replica-GreenCoop.js

⚠️ Attendre que le Replica Set devienne PRIMARY avant de passer aux insertions.

## Étape 3 - Tester
Connectez-vous :
mongosh --port 27017
ou avec l’utilisateur analyste :
mongosh --port 27017 -u analyste -p readonly123 --authenticationDatabase admin

## Étape 4 - Arrêter proprement
.\stop-replica-GreenCoop.ps1
