// Initialisation du Replica Set
rs.initiate({
  _id: "rsGreenCoop",
  members: [
    { _id: 0, host: "mongo1:27017", priority: 2 },
    { _id: 1, host: "mongo2:27017", priority: 0.5 },
    { _id: 2, host: "mongo3:27017", priority: 0.5 }
  ]
})

// Vérifier l'état
rs.status()

// Sélection explicite de la base admin (mongosh compatible)
const adminDb = db.getSiblingDB("admin")

// Création de l'utilisateur read-only
// adminDb.createUser({
//  user: "analyste",
//  pwd: "readonly123",
//  roles: [
//    {
//      role: "read",
//      db: "GreenCoop"
//    }
// ]
// })
