FROM jupyter/base-notebook

# Définir le répertoire de travail
WORKDIR /home/jovyan/app

# Copier les dossiers nécessaires dans l'image
COPY ./data ./data
COPY ./migration/restore_and_visualize.py ./migration/
COPY ./scripts-replica/wait_for_mongo_primary.py ./scripts-replica/

# Installer les dépendances Python
RUN pip install pandas matplotlib pymongo openpyxl

# Définir l'exécution automatique
ENV PYTHONUNBUFFERED=1

# Commande lancée automatiquement au démarrage du conteneur
CMD python scripts-replica/wait_for_mongo_primary.py && \
    python migration/restore_and_visualize.py
