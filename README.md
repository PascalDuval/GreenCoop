# GreenCoop - Migration data meteo et dockerisation

Ce projet couvre deux volets:

1. Besoin metier data
  - restauration d un backup JSONL dans MongoDB Time Series,
  - controles d integrite et tests CRUD,
  - generation d un graphe de temperature.

2. Industrialisation technique
  - cluster MongoDB Replica Set (3 noeuds),
  - orchestration Docker Compose,
  - automatisation des tests migration + replica,
  - documentation de deploiement (EC2/ECR/monitoring).

## 1) Cloner le depot

```bash
git clone https://github.com/PascalDuval/GreenCoop.git
cd GreenCoop
```

## 2) Prerequis

- Docker Desktop (obligatoire)
- Git
- Optionnel: mongosh (pour script PowerShell tout-en-un)
- Optionnel: Python 3.11+ pour execution locale hors Docker
- Optionnel: Jupyter Notebook/Lab pour explorer les notebooks legacy

## 3) Arborescence utile

```text
GreenCoop/
  docker-compose.yml
  docker-compose-minimal.yml
  Dockerfile
  run-all-replica.ps1
  migration/                # code Python de migration + tests
  scripts-replica/          # scripts de setup/test replica
  data/                     # backup et sorties locales
  docs/                     # documentation consolidee
  archive/legacy-ancien/    # historique (anciens notebooks/scripts)
```

## 4) Variables d environnement

Le projet fonctionne sans configuration grace aux valeurs par defaut du compose.
Pour personnaliser, copiez le fichier d exemple:

```powershell
Copy-Item .env.example .env
```

Puis adaptez les valeurs dans .env.

Variables principales:

- ENABLE_REPLICA_TESTS
- MONGO_URI
- MONGO_PRIMARY_URI
- MONGO_PRIMARY_ADMIN_URI
- MONGO_REPLICA_URI
- MONGO_CLONE_SECONDARY_URI
- DB_NAME
- COLLECTION_NAME
- BACKUP_FILE
- VISUAL_FILE

## 5) Lancer le projet en local (recommande)

### Option A - Tout avec Docker (recommande)

```powershell
docker compose up -d --build
docker compose logs -f
```

Le conteneur data_migration execute:

1. attente du PRIMARY,
2. restauration du backup,
3. generation du graphe,
4. tests migration,
5. tests replica.

Relancer les tests uniquement:

```powershell
docker start -a data_migration
```

Arreter/nettoyer:

```powershell
docker compose down -v
```

Ports Mongo exposes:

- PRIMARY: localhost:27027
- SECONDARY: localhost:27028
- SECONDARY: localhost:27029

### Option B - Script Windows tout-en-un

```powershell
$env:MONGOSH_PATH="C:\path\to\mongosh.exe"
.\run-all-replica.ps1
```

## 6) Execution locale Python (sans Docker)

Installez les dependances:

```powershell
pip install pymongo pandas matplotlib
```

Puis executez:

```powershell
python -m migration.restore_backup_and_plot
python -m migration.run_migration_tests
```

Note: en execution hors Docker, MongoDB doit etre accessible sur les URI configurees.

## 7) Jupyter

Les notebooks historiques sont dans:

- archive/legacy-ancien/notebooks
- archive/legacy-ancien/fonction_gen_CRUD.ipynb

Exemple de lancement:

```powershell
jupyter lab
```

Puis ouvrez les notebooks depuis l arborescence archive/legacy-ancien.

Si vous utilisez un environnement conda dedie, selectionnez le kernel correspondant avant execution.

## 8) Documentation

- docs/deployment/PROCEDURE_EC2.md
- docs/deployment/
- docs/architecture/
- docs/presentation/
- docs/notes/

## 9) Historique et archives

- archive/legacy-ancien: ancien perimetre conserve
- archive/old-docs: anciennes versions de livrables
