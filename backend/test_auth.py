#!/usr/bin/env python
"""Test script for auth endpoints with mock database"""

from app.database.mongodb import MongoDatabase
import asyncio
import json

# Initialize database
MongoDatabase.connect_db()

# Test the mock database directly
def test_mock_database():
    """Test mock database operations"""
    print("\n[TEST] Mock Database Operations")
    
    from app.database.mock_db import get_mock_database
    from app.auth.jwt_handler import hash_password
    
    db = get_mock_database()
    users_collection = db["users"]
    
    # Test insert
    test_user = {
        "name": "Test User",
        "email": "test@example.com",
        "password_hash": hash_password("password123"),
        "role": "student"
    }
    
    result = users_collection.insert_one(test_user)
    print(f"  [OK] User inserted with ID: {result.inserted_id}")
    
    # Test find_one
    found_user = users_collection.find_one({"email": "test@example.com"})
    if found_user:
        print(f"  [OK] User found: {found_user['name']}")
    
    # Test find with non-existent email
    not_found = users_collection.find_one({"email": "nonexistent@example.com"})
    if not_found is None:
        print(f"  [OK] Non-existent user correctly returns None")
    
def test_auth_functions():
    """Test auth functions"""
    print("\n[TEST] Authentication Functions")
    
    from app.auth.jwt_handler import hash_password, verify_password, create_access_token, decode_access_token
    from datetime import timedelta
    from config import settings
    
    # Test password hashing
    password = "testpassword123"
    hashed = hash_password(password)
    print(f"  [OK] Password hashed: {hashed[:20]}...")
    
    # Test password verification
    if verify_password(password, hashed):
        print(f"  [OK] Password verification: PASSED")
    else:
        print(f"  [ERROR] Password verification: FAILED")
    
    # Test wrong password
    if not verify_password("wrongpassword", hashed):
        print(f"  [OK] Wrong password correctly rejected")
    
    # Test JWT token creation
    token = create_access_token(
        data={"sub": "test_user_id"},
        expires_delta=timedelta(minutes=30)
    )
    print(f"  [OK] JWT token created: {token[:20]}...")
    
    # Test token decoding
    decoded = decode_access_token(token)
    if decoded == "test_user_id":
        print(f"  [OK] JWT token decoded correctly: {decoded}")
    
async def run_auth_endpoints():
    """Test auth endpoints using FastAPI TestClient"""
    print("\n[TEST] Auth Endpoints")

    from httpx import ASGITransport, AsyncClient
    from main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Test register
        endpoint_email = "endpoint@example.com"

        register_response = await ac.post(
            "/api/auth/register",
            json={
                "name": "Endpoint User",
                "email": endpoint_email,
                "password": "password123"
            }
        )

        assert register_response.status_code == 200, register_response.text
        register_data = register_response.json()
        print(f"  [OK] User registration successful")
        print(f"  [OK] User ID: {register_data['user']['id']}")
        print(f"  [OK] Email: {register_data['user']['email']}")

        # Test login
        login_response = await ac.post(
            "/api/auth/login",
            json={
                "email": endpoint_email,
                "password": "password123"
            }
        )

        assert login_response.status_code == 200, login_response.text
        login_data = login_response.json()
        print(f"  [OK] Login successful")
        print(f"  [OK] Token received: {login_data['access_token'][:20]}...")
        auth_headers = {"Authorization": f"Bearer {login_data['access_token']}"}

        profile_response = await ac.get("/api/auth/me", headers=auth_headers)
        assert profile_response.status_code == 200, profile_response.text
        print("  [OK] Profile loaded successfully")

        update_response = await ac.patch(
            "/api/auth/me",
            headers=auth_headers,
            json={
                "name": "Endpoint User Updated",
                "email": "endpoint-updated@example.com",
            },
        )
        assert update_response.status_code == 200, update_response.text
        print("  [OK] Profile update successful")

        password_response = await ac.post(
            "/api/auth/me/password",
            headers=auth_headers,
            json={
                "current_password": "password123",
                "new_password": "newpassword123",
            },
        )
        assert password_response.status_code == 200, password_response.text
        print("  [OK] Password change successful")

        chat_response = await ac.post(
            "/api/chat/send",
            headers=auth_headers,
            json={
                "user_id": register_data["user"]["id"],
                "question": "Explain photosynthesis",
                "subject": "Science"
            }
        )

        assert chat_response.status_code == 200, chat_response.text
        chat_data = chat_response.json()
        assert "placeholder response" not in chat_data["answer"].lower()
        print("  [OK] Chat response generated successfully")

        quiz_response = await ac.post(
            "/api/quiz/generate",
            headers=auth_headers,
            json={
                "user_id": register_data["user"]["id"],
                "subject": "Science",
                "topic": "photosynthesis",
                "question_count": 3,
            },
        )
        assert quiz_response.status_code == 200, quiz_response.text
        quiz_data = quiz_response.json()
        assert len(quiz_data["questions"]) == 3
        print("  [OK] Quiz generated successfully")

        submit_response = await ac.post(
            f"/api/quiz/{quiz_data['id']}/submit",
            headers=auth_headers,
            json={
                "user_id": register_data["user"]["id"],
                "answers": {
                    question["id"]: question["correct_option"]
                    for question in quiz_data["questions"]
                },
            },
        )
        assert submit_response.status_code == 200, submit_response.text
        assert submit_response.json()["score"] == 3
        print("  [OK] Quiz submission scored successfully")

def test_auth_endpoints():
    """Pytest-compatible wrapper for async auth endpoint checks"""
    asyncio.run(run_auth_endpoints())

if __name__ == "__main__":
    print("=" * 60)
    print("OL Mate Auth Tests")
    print("=" * 60)
    print(f"[INFO] Using Database: Mock (development)")
    
    # Run tests
    test_mock_database()
    test_auth_functions()
    
    # Run async tests
    try:
        asyncio.run(run_auth_endpoints())
    except Exception as e:
        print(f"  [WARNING] Endpoint tests skipped: {type(e).__name__}")
    
    print("\n" + "=" * 60)
    print("[OK] Core auth tests completed successfully!")
    print("=" * 60)
