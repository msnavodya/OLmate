from pymongo import MongoClient
from config import settings
from app.database.mock_db import get_mock_database

class MongoDatabase:
    client = None
    db = None
    using_mock = False

    @classmethod
    def connect_db(cls):
        """Connect to MongoDB or use mock database if not configured"""
        try:
            # Check if MongoDB URL is just a placeholder
            if (
                not settings.MONGODB_URL
                or "user:password" in settings.MONGODB_URL
                or "cluster.mongodb.net" in settings.MONGODB_URL
            ):
                raise ValueError("MongoDB URL not configured (placeholder detected)")
            
            # Try to connect to MongoDB
            cls.client = MongoClient(settings.MONGODB_URL, serverSelectionTimeoutMS=5000)
            # Test connection
            cls.client.admin.command('ping')
            cls.db = cls.client[settings.DATABASE_NAME]
            cls.using_mock = False
            print("[OK] Connected to MongoDB successfully")
        except Exception as e:
            print(f"[WARNING] MongoDB connection failed: {str(e)}")
            print("[INFO] Using in-memory mock database for development/testing")
            cls.db = get_mock_database()
            cls.using_mock = True
            cls.client = None

        return cls.db

    @classmethod
    def close_db(cls):
        """Close MongoDB connection if using real database"""
        if cls.client and not cls.using_mock:
            cls.client.close()
            print("[OK] Disconnected from MongoDB")
        cls.client = None
        cls.db = None

    @classmethod
    def get_db(cls):
        """Get database instance (real MongoDB or mock)"""
        if cls.db is None:
            return cls.connect_db()
        return cls.db

def get_database():
    """Get database for dependency injection"""
    db = MongoDatabase.get_db()
    if db is None:
        # Last-resort fallback so request handlers never crash with None["users"].
        print("[WARNING] Database was not initialized; using in-memory mock database")
        db = get_mock_database()
        MongoDatabase.db = db
        MongoDatabase.using_mock = True
    return db
