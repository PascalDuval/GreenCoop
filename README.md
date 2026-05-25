# GreenCoop - Migration de données météo et dockerisation

Ce dépôt couvre deux parties principales:

1. Réponse au besoin métier data
   - restauration d'un backup JSONL dans MongoDB Time Series,
   - contrôles d'intégrité,
   - tests CRUD,
   - génération d'un graphique de température.

2. Industrialisation technique
   - cluster MongoDB Replica Set (3 nœuds),
   - orchestration Docker Compose,
   - automatisation des tests migration + réplication,
   - documentation de déploiement (EC2/ECR/monitoring).

## 1) Cloner le dépôt

```bash
git clone https://github.com/PascalDuval/GreenCoop.git
cd GreenCoop
```

## 2) Prérequis

- Docker Desktop (obligatoire)
- Git
- Optionnel: mongosh (pour le script PowerShell tout-en-un)
- Optionnel: Python 3.11+ pour exécution locale hors Docker
- Optionnel: Jupyter Notebook/Lab pour explorer les notebooks historiques

## 3) Arborescence utile

```text
GreenCoop/
  docker-compose.yml
  docker-compose-minimal.yml
  Dockerfile
  run-all-replica.ps1
  migration/                # code Python de migration + tests
  scripts-replica/          # scripts de setup/test Replica Set
  data/                     # backup et sorties locales
  docs/
    deployment/
    architecture/
  archive/legacy-ancien/    # historique (anciens notebooks/scripts)
```

## 4) Variables d'environnement

Le projet fonctionne sans configuration grâce aux valeurs par défaut du compose.
Pour personnaliser:

```powershell
Copy-Item .env.example .env
```

Puis adaptez les valeurs de `.env`.

Variables principales:

- `ENABLE_REPLICA_TESTS`
- `MONGO_URI`
- `MONGO_PRIMARY_URI`
- `MONGO_PRIMARY_ADMIN_URI`
- `MONGO_REPLICA_URI`
- `MONGO_CLONE_SECONDARY_URI`
- `DB_NAME`
- `COLLECTION_NAME`
- `BACKUP_FILE`
- `VISUAL_FILE`

## 5) Démarrage local (recommandé)

### Option A - Full Docker

```powershell
docker compose up -d --build
docker compose logs -f
```

Le conteneur `data_migration` exécute automatiquement:

1. attente du PRIMARY,
2. restauration du backup,
3. génération du graphe,
4. tests de migration,
5. tests de réplication.

Relancer uniquement la partie tests/migration:

```powershell
docker start -a data_migration
```

Arrêter/nettoyer:

```powershell
docker compose down -v
```

Ports MongoDB exposés:

- PRIMARY: `localhost:27027`
- SECONDARY: `localhost:27028`
- SECONDARY: `localhost:27029`

### Option B - Script Windows tout-en-un

```powershell
$env:MONGOSH_PATH="C:\path\to\mongosh.exe"
.\run-all-replica.ps1
```

## 6) Fonctionnement détaillé des scripts

### Scripts d'orchestration

- `run-all-replica.ps1`
  - stoppe l'existant (`docker compose down -v`),
  - relance les conteneurs (`docker compose up -d --build`),
  - initialise le Replica Set via `scripts-replica/init-replica-GreenCoop.js`,
  - crée les utilisateurs via `scripts-replica/create-users.js`,
  - vérifie l'accès en lecture sur un secondaire,
  - exécute le conteneur `data_migration`.

- `scripts-replica/mongo-setup.sh`
  - attend que `mongo1` réponde,
  - initialise le Replica Set,
  - attend l'élection du PRIMARY,
  - crée les utilisateurs applicatifs.

### Scripts de migration Python

- `migration/restore_backup_and_plot.py`
  - lit `data/backup_ObsProEtAmateur.jsonl`,
  - remplace le contenu de la collection cible,
  - génère le graphique `data/visualisation_temp.png`.

- `migration/run_migration_tests.py`
  - exécute les tests de migration dans cet ordre:
    - intégrité (`test_integrity`),
    - lecture (`test_crud_read`),
    - insertion/suppression (`test_crud_insert_delete`).

### Scripts de tests Replica Set

- `scripts-replica/run_replica_tests.py`
  - vérifie l'état du Replica Set,
  - vérifie l'accès admin au PRIMARY,
  - vérifie la lecture en SECONDARY,
  - vérifie la lecture read-only sur un nœud secondaire cloné.

## 7) Exécution locale Python (sans Docker)

Installer les dépendances:

```powershell
pip install pymongo pandas matplotlib
```

Exécuter:

```powershell
python -m migration.restore_backup_and_plot
python -m migration.run_migration_tests
```

Note: en exécution hors Docker, MongoDB doit être accessible via les URI configurées.

## 8) Jupyter

Notebooks historiques disponibles dans:

- `archive/legacy-ancien/notebooks`
- `archive/legacy-ancien/fonction_gen_CRUD.ipynb`

Lancement:

```powershell
jupyter lab
```

Ensuite, ouvrir les notebooks depuis `archive/legacy-ancien`.

Conseil: si vous utilisez un environnement Conda dédié, sélectionnez le kernel correspondant avant exécution.

## 9) Documentation

- `docs/deployment/PROCEDURE_EC2.md`
- `docs/deployment/`
- `docs/architecture/`

## 10) Historique et archives

- `archive/legacy-ancien`: ancien périmètre conservé
- `archive/old-docs`: anciennes versions de livrables
