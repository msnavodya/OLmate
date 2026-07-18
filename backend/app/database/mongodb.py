from pymongo import MongoClient
from config import settings

class MongoDatabase:
    client = None
    db = None

    @classmethod
    def connect_db(cls):
        cls.client = MongoClient(settings.MONGODB_URL)
        cls.db = cls.client[settings.DATABASE_NAME]
        print("✓ Connected to MongoDB")

    @classmethod
    def close_db(cls):
        if cls.client:
            cls.client.close()
            print("✗ Disconnected from MongoDB")

    @classmethod
    def get_db(cls):
        return cls.db

def get_database():
    return MongoDatabase.get_db()
