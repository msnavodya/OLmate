from app.database.mongodb import get_database, MongoDatabase


def main():
    db = get_database()
    using_mock = getattr(MongoDatabase, 'using_mock', False)

    if using_mock:
        # db is a MockDatabase instance
        try:
            users_before = len(db.collections.get('users', []))
            db.collections['users'] = []
            print(f"Mock DB: deleted {users_before} user(s)")
            return
        except Exception as exc:
            print(f"Mock DB deletion failed: {exc}")
            return

    # If we reach here, treat db as a PyMongo database
    try:
        result = db['users'].delete_many({})
        print(f"MongoDB: deleted {getattr(result, 'deleted_count', 'unknown')} user(s)")
    except Exception as exc:
        print(f"MongoDB deletion failed: {exc}")


if __name__ == '__main__':
    main()
