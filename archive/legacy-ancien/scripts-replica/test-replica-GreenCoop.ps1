====================================================
README – Tests du Replica Set MongoDB GreenCoop
====================================================

Ce document décrit PAS À PAS :
- le lancement du Replica Set MongoDB
- son initialisation
- les tests fonctionnels (écriture, lecture, panne)
- l’arrêt et le nettoyage

Contexte :
- Base : GreenCoop
- Collection : ObsProEtAmateur
- Type : Time Series
  - timeField : dh_utc
  - metaField : station_id
- Replica Set : rsGreenCoop
- Environnement : Windows + PowerShell + MongoDB 8.x

----------------------------------------------------
1. STRUCTURE DES SCRIPTS
----------------------------------------------------

Dossier :
C:\Users\karap\OpenClassRooms\dataprojet8\scripts

Fichiers :
- start-replica-GreenCoop.ps1     -> démarre les 3 nœuds mongod
- init-replica-GreenCoop.ps1      -> initialise le replica set + utilisateurs
- test-replica-GreenCoop.ps1      -> lance tous les tests
- stop-replica-GreenCoop.ps1      -> arrête tous les mongod
- README_Test-Replica-GreenCoop.txt

----------------------------------------------------
2. ARCHITECTURE DU REPLICA SET
----------------------------------------------------

Replica Set : rsGreenCoop

Nœuds :
- PRIMARY
  - Port : 27017
  - Droits : lecture / écriture
  - Usage : ingestion des données météo (time series)

- ANALYSTE (SECONDARY)
  - Port : 27018
  - Droits : lecture seule
  - Usage : analyses, requêtes, notebooks

- SECONDARY_CLONE
  - Port : 27019
  - Droits : aucun utilisateur
  - Usage : secours / promotion possible en PRIMARY

IMPORTANT :
- Pas d’arbiter ici car nous avons déjà 3 nœuds.
- Cela garantit un quorum et une élection automatique.

----------------------------------------------------
3. LANCEMENT DU REPLICA SET
----------------------------------------------------

Ouvrir PowerShell (mode normal ou admin).

Se placer dans le dossier scripts :

cd C:\Users\karap\OpenClassRooms\dataprojet8\scripts

Lancer les 3 nœuds MongoDB :

.\start-replica-GreenCoop.ps1

Résultat attendu :
- 3 fenêtres mongod ouvertes
- Ports 27017, 27018, 27019 en écoute

----------------------------------------------------
4. INITIALISATION DU REPLICA SET
----------------------------------------------------

Toujours dans le dossier scripts :

.\init-replica-GreenCoop.ps1

Ce script :
- exécute rs.initiate()
- définit les priorités des nœuds
- crée un utilisateur "analyste" en lecture seule

Utilisateur créé :
- user : analyste
- password : readonly123
- rôle : read sur la base GreenCoop

Vérification possible :

mongosh --port 27017
rs.status()

----------------------------------------------------
5. LANCEMENT DES TESTS AUTOMATISÉS
----------------------------------------------------

Lancer le script de test :

.\test-replica-GreenCoop.ps1

Le script exécute les tests suivants :

TEST 1
Insertion sur le PRIMARY (27017)
→ DOIT RÉUSSIR

TEST 2
Lecture sur le SECONDARY ANALYSTE (27018)
→ DOIT RÉUSSIR

TEST 3
Tentative d’insertion sur ANALYSTE
→ DOIT ÉCHOUER (read-only)

TEST 4
Simulation de panne du PRIMARY
→ insertion impossible
→ lecture toujours possible sur SECONDARY

TEST 5
Redémarrage du PRIMARY
→ reprise normale des insertions

Le script te demandera :
- d’éteindre manuellement le PRIMARY
- puis de le redémarrer avant de continuer

----------------------------------------------------
6. SIMULATION DE PANNE MANUELLE
----------------------------------------------------

Méthode simple :

- Fermer la fenêtre mongod du port 27017
OU
- Tuer le process via le Gestionnaire de tâches

MongoDB élira automatiquement un nouveau PRIMARY
(si les conditions sont réunies).

----------------------------------------------------
7. ARRÊT COMPLET DU REPLICA SET
----------------------------------------------------

Arrêt propre via script :

.\stop-replica-GreenCoop.ps1

Ou arrêt manuel :

Stop-Process -Name mongod -Force

----------------------------------------------------
8. NETTOYAGE COMPLET DES DONNÉES
----------------------------------------------------

ATTENTION : SUPPRESSION DÉFINITIVE DES DONNÉES

Remove-Item -Recurse -Force C:\Users\karap\mongodb\rs-*

À utiliser uniquement pour repartir de zéro.

----------------------------------------------------
9. VÉRIFICATION AVEC MONGODB COMPASS
----------------------------------------------------

Connexion possible à :
- mongodb://localhost:27017 (PRIMARY)
- mongodb://localhost:27018 (SECONDARY – lecture)

Vérifier :
- état PRIMARY / SECONDARY
- réplication des documents
- collection time-series ObsProEtAmateur

----------------------------------------------------
10. POURQUOI LE REPLICA SET EST ADAPTÉ
----------------------------------------------------

Avantages :
- Haute disponibilité
- Séparation ingestion / analyse
- Sécurité par rôles utilisateurs
- Tolérance aux pannes
- Parfait pour des données time-series météo

Cas pédagogique idéal :
- démonstration de panne
- reprise automatique
- lecture continue malgré l’indisponibilité du PRIMARY

----------------------------------------------------
FIN DU DOCUMENT
----------------------------------------------------
