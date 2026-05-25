from pymongo import MongoClient

from migration.config import COLLECTION_NAME, DB_NAME, MONGO_URI


class TimeSeriesManager:
    def __init__(self, uri=None, db_name=None, collection_name=None):
        self.uri = uri or MONGO_URI
        self.db_name = db_name or DB_NAME
        self.collection_name = collection_name or COLLECTION_NAME
        self.client = MongoClient(self.uri, serverSelectionTimeoutMS=10000)
        self.db = self.client[self.db_name]
        self.collection = self.db[self.collection_name]

    def ping(self):
        self.client.admin.command("ping")

    def insert(self, docs):
        if isinstance(docs, dict):
            result = self.collection.insert_one(docs)
            return result.inserted_id
        if isinstance(docs, list):
            result = self.collection.insert_many(docs)
            return result.inserted_ids
        raise ValueError("insert expects a dict or a list of dicts")

    def read(self, filter_query=None, limit=10, projection=None, sort=None):
        query = filter_query or {}
        cursor = self.collection.find(query, projection)
        if sort:
            cursor = cursor.sort(sort)
        if limit:
            cursor = cursor.limit(limit)
        return list(cursor)

    def count(self, filter_query=None):
        query = filter_query or {}
        return self.collection.count_documents(query)

    def delete(self, filter_query):
        query = filter_query or {}
        return self.collection.delete_many(query)

    def correct_measure(self, filter_query, new_doc):
        deleted = self.delete(filter_query)
        inserted_id = self.insert(new_doc)
        return deleted.deleted_count, inserted_id

    def to_dataframe(self, filter_query=None, limit=0):
        import pandas as pd

        query = filter_query or {}
        cursor = self.collection.find(query)
        if limit:
            cursor = cursor.limit(limit)
        data = list(cursor)
        return pd.DataFrame(data)

    def replace_all(self, docs):
        self.collection.delete_many({})
        if docs:
            self.collection.insert_many(docs)

    def close(self):
        self.client.close()
