PROCESSUS DE COLLECTE, TRANSFORMATION ET STOCKAGE DES DONNÉES MÉTÉOROLOGIQUES
Projet : POC Data Météo

---

1. COLLECTE DES DONNÉES
   (Source : bucket local Airbyte)

Les différentes sources de données météorologiques, professionnelles (InfoClimat) et amateurs (Weather Underground), sont centralisées dans un bucket local Airbyte, utilisé comme point d’entrée unifié dans le cadre d’un POC.

Formats de données en entrée :

* Fichiers JSON : observations issues des stations professionnelles InfoClimat
* Fichiers XLSX : observations issues des stations amateurs Weather Underground

---

2. TRANSFORMATION ET CONTRÔLE DE QUALITÉ
   (ETL local en Python)

Les données sont traitées via un pipeline de transformation local implémenté dans un script Jupyter Notebook.

2.a Parsing et normalisation

* Conversion des fichiers XLSX en structures tabulaires à l’aide de pandas
* Standardisation des formats de date (champ dh_utc)
* Harmonisation des unités de mesure (ex. inHg vers hPa)
* Normalisation des noms de champs en français
* Fusion des observations amateurs et professionnelles dans un format de données unifié

2.b Ajout des métadonnées

* Ajout des informations liées aux stations :
  identifiant de station, localisation, type de station, matériel, logiciel, source
* Normalisation des identifiants station_id pour garantir un suivi homogène

2.c Tests d’intégrité et nettoyage

* Vérification des types de données et des colonnes attendues
* Détection des doublons
* Analyse et suppression des valeurs aberrantes (ex. températures extrêmes, pressions incohérentes)
* Génération du fichier final nettoyé au format JSON :
  observations_flat.json

---

3. STOCKAGE DANS MONGODB (TIME SERIES)

Le fichier JSON nettoyé est importé dans une instance MongoDB locale configurée en collection de type Time Series.

Paramètres principaux :

* Collection unique de type Time Series
* Champ temporel (timeField) : dh_utc
* Champ méta (metaField) : station_id

Cette modélisation permet :

* des lectures et insertions optimisées par station et par période
* des corrections ciblées via un module CRUD dédié (ts_crud.py)
* une structure extensible et compatible avec MongoDB Atlas et MongoDB Charts

---

4. Structure Dockerisée

* rédaction de docker-compose.yml : orchestration de 4 services distincts (mongo1 - mongo2 - mongo3 - data_migration)
* rédaction de Dockerfile : Construit l'image pour le conteneur data_migration

A la fin on a : 

* Un cluster MongoDB répliqué et opérationnel,
* Une base de données restaurée automatiquement,
* Des vérifications effectuées,
* Une visualisation prête à l’usage,
* Le tout conteneurisé et réutilisable facilement


5. Mise en exploitation de l'application Dockerisée sur AWS.

* Phase 1 : Repository créé et Image poussé sur Amazon ECR
* Phase 2 : Paramétrage
 	   - d'une Task Definition MongoDB
	   - d'un Service MongoDB ECS
	   - de la Sécurité réseau
* Phase 3 : Lancement
* Phase 4 : Logs & Monitoring
	   - Logs applicatifs
	   - Métriques systèmes
	   - Reporting métier
* Phase 5 : Sauvegardes automatiques (Task ECS planifiée qui fait mongodump)



---




RÉSUMÉ DU PROCESSUS

Étape 1 – Collecte
Récupération des données depuis les sources météo vers Airbyte local

Étape 2 – Transformation
Nettoyage, standardisation et contrôle qualité via Python

Étape 3 – Stockage
Importation dans MongoDB via une collection Time Series

Étape 4 – Réexposition
Données réinjectées dans Airbyte pour les tests POC

---

