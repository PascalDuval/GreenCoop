#!/bin/sh
set -e

echo "mongo-setup: waiting for mongo1..."
i=1
while [ "$i" -le 30 ]; do
  if mongosh --host mongo1:27017 --eval "db.adminCommand({ ping: 1 })" >/dev/null 2>&1; then
    break
  fi
  i=$((i+1))
  sleep 2
done

echo "mongo-setup: init replica set"
mongosh --host mongo1:27017 /scripts/init-replica-GreenCoop.js

echo "mongo-setup: waiting for PRIMARY..."
i=1
while [ "$i" -le 30 ]; do
  if mongosh --host mongo1:27017 --eval "rs.isMaster().ismaster" | grep -q "true"; then
    break
  fi
  i=$((i+1))
  sleep 2
done

echo "mongo-setup: create users"
mongosh --host mongo1:27017 /scripts/create-users.js

echo "mongo-setup: done"
