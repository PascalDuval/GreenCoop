# migration/check_migration.py

from crud_utils import get_collection, count_documents
from pymongo.errors import ConnectionFailure

def run_check():
    print("🚀 Vérification de la migration en cours...\n")

    try:
        # Connexion à la collection
        collection = get_collection()

        # Comptage des documents
        nb_docs = count_documents(collection)

        # Règle de validation arbitraire
        if nb_docs == 0:
            print("❌ ERREUR : Aucun document trouvé dans la collection.")
        else:
            print(f"✅ Migration OK : {nb_docs} documents présents.")

    except ConnectionFailure as e:
        print(f"❌ Impossible de se connecter à MongoDB : {e}")

    except Exception as e:
        print(f"❌ Erreur pendant le check : {e}")


if __name__ == "__main__":
    run_check()
