# Dockerfile

FROM python:3.11-slim-bookworm

WORKDIR /home/jovyan/app

# Copy scripts and data used by the container
COPY ./migration ./migration
COPY ./scripts-replica ./scripts-replica
COPY ./data ./data

# Install runtime dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libfreetype6 \
        libpng16-16 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pymongo pandas matplotlib

# Ensure unbuffered logs
ENV PYTHONUNBUFFERED=1

# Wait for PRIMARY and run tests
CMD ["sh", "-c", "\
    python3 scripts-replica/wait_for_mongo_primary.py && \
    python3 -m migration.restore_backup_and_plot && \
    python3 -m migration.run_migration_tests && \
    python3 scripts-replica/run_replica_tests.py \
"]
