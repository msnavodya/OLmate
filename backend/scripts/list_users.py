from app.database.mongodb import get_database, MongoDatabase


def main():
    db = get_database()
    using_mock = getattr(MongoDatabase, 'using_mock', False)
    print(f"using_mock={using_mock}")

    try:
        users = list(db['users'].find({}, projection={'password_hash': 0}))
    except Exception:
        # MockCollection returns list directly
        users = db['users'].find()

    print(f"user_count={len(users)}")
    for u in users:
        print(u.get('email') if isinstance(u, dict) else getattr(u, 'email', str(u)))


if __name__ == '__main__':
    main()
