"""
Mock in-memory database for development/testing
Used when MongoDB is not configured
"""
from datetime import datetime
from bson.objectid import ObjectId
from typing import Optional, Dict, List, Any

class MockDatabase:
    """In-memory mock database that mimics MongoDB behavior"""
    
    def __init__(self):
        self.collections = {
            "users": [],
            "chats": [],
            "documents": []
        }
    
    def __getitem__(self, collection_name: str):
        """Get a collection"""
        if collection_name not in self.collections:
            self.collections[collection_name] = []
        return MockCollection(self.collections[collection_name])

class MockCollection:
    """Mock MongoDB collection with basic operations"""
    
    def __init__(self, data: List[Dict]):
        self.data = data
    
    def find_one(self, query: Dict[str, Any]) -> Optional[Dict]:
        """Find one document matching the query"""
        for doc in self.data:
            if self._matches_query(doc, query):
                return doc
        return None
    
    def find(
        self,
        query: Optional[Dict[str, Any]] = None,
        projection: Optional[Dict[str, Any]] = None,
        sort: Optional[List[tuple]] = None,
    ) -> List[Dict]:
        """Find all documents matching the query"""
        if query is None:
            result = list(self.data)
        else:
            result = []
            for doc in self.data:
                if self._matches_query(doc, query):
                    result.append(doc)

        if sort:
            for field, direction in reversed(sort):
                result.sort(
                    key=lambda doc: doc.get(field),
                    reverse=direction == -1,
                )

        if projection:
            result = [self._apply_projection(doc, projection) for doc in result]
        
        return result
    
    def insert_one(self, document: Dict) -> 'MockInsertResult':
        """Insert a single document"""
        doc_id = ObjectId()
        document["_id"] = doc_id
        self.data.append(document)
        return MockInsertResult(doc_id)
    
    def delete_one(self, query: Dict[str, Any]) -> 'MockDeleteResult':
        """Delete a single document"""
        for i, doc in enumerate(self.data):
            if self._matches_query(doc, query):
                self.data.pop(i)
                return MockDeleteResult(deleted_count=1)
        return MockDeleteResult(deleted_count=0)
    
    def update_one(self, query: Dict[str, Any], update: Dict) -> 'MockUpdateResult':
        """Update a single document"""
        for doc in self.data:
            if self._matches_query(doc, query):
                if "$set" in update:
                    doc.update(update["$set"])
                else:
                    doc.update(update)
                return MockUpdateResult(modified_count=1)
        return MockUpdateResult(modified_count=0)

    def count_documents(self, query: Dict[str, Any]) -> int:
        """Count documents matching the query"""
        return len(self.find(query))

    def _apply_projection(self, doc: Dict, projection: Dict[str, Any]) -> Dict:
        """Apply simple MongoDB-style include/exclude projection"""
        projected = dict(doc)
        excluded_fields = [key for key, value in projection.items() if value == 0]

        for field in excluded_fields:
            projected.pop(field, None)

        return projected
    
    def _matches_query(self, doc: Dict, query: Dict) -> bool:
        """Check if document matches query"""
        for key, value in query.items():
            if key not in doc:
                return False
            if isinstance(value, dict):
                # Handle operators like $eq, $gt, etc.
                for op, val in value.items():
                    if op == "$eq" and doc[key] != val:
                        return False
                    elif op == "$ne" and doc[key] == val:
                        return False
                    elif op == "$gt" and doc[key] <= val:
                        return False
            else:
                if doc[key] != value:
                    return False
        return True

class MockInsertResult:
    """Mock MongoDB insert result"""
    
    def __init__(self, inserted_id):
        self.inserted_id = inserted_id

class MockDeleteResult:
    """Mock MongoDB delete result"""
    
    def __init__(self, deleted_count: int = 0):
        self.deleted_count = deleted_count

class MockUpdateResult:
    """Mock MongoDB update result"""
    
    def __init__(self, modified_count: int = 0):
        self.modified_count = modified_count

# Global mock database instance (shared across requests)
_mock_db_instance = None

def get_mock_database():
    """Get or create global mock database instance"""
    global _mock_db_instance
    if _mock_db_instance is None:
        _mock_db_instance = MockDatabase()
    return _mock_db_instance
