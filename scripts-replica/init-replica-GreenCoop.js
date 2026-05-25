// init-replica-GreenCoop.js

try {
  rs.status();
  print("init-replica: replica set already initialized");
} catch (err) {
  print("init-replica: initializing replica set");
  rs.initiate({
    _id: "rsGreenCoop",
    members: [
      { _id: 0, host: "mongo1:27017", priority: 2 },
      { _id: 1, host: "mongo2:27017", priority: 1 },
      { _id: 2, host: "mongo3:27017", priority: 1 },
    ],
  });
}

rs.status();
