// create-users.js

const adminDb = db.getSiblingDB("admin");
const appDb = db.getSiblingDB("GreenCoop");

if (!adminDb.getUser("admin")) {
  print("create-users: creating admin user");
  adminDb.createUser({
    user: "admin",
    pwd: "admin123",
    roles: [{ role: "root", db: "admin" }],
  });
} else {
  print("create-users: admin user already exists");
}

if (!appDb.getUser("analyste")) {
  print("create-users: creating analyst user");
  appDb.createUser({
    user: "analyste",
    pwd: "readonly123",
    roles: [{ role: "read", db: "GreenCoop" }],
  });
} else {
  print("create-users: analyst user already exists");
}
