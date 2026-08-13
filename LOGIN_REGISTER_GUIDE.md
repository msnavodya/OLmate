# Login & Register Setup Guide

## ✅ Fixed! Login and Register Now Work Without MongoDB

The backend has been configured to use an **in-memory mock database** for development/testing. This means you can now **login and register** without needing to configure MongoDB!

---

## 🚀 Quick Start

### 1. Start Backend Server

```bash
cd backend
python -m venv venv
. .\venv\Scripts\Activate.ps1
python main.py
```

You should see:
```
[WARNING] MongoDB connection failed: MongoDB URL not configured (placeholder detected)
[INFO] Using in-memory mock database for development/testing
[OK] Backend started on http://localhost:8000
```

### 2. Start Frontend

```bash
cd frontend
npm run dev
```

Open: **http://localhost:5173**

### 3. Register New User

- Go to **Register page**
- Fill in:
  - **Name**: Any name (e.g., "Test User")
  - **Email**: Any email (e.g., "test@example.com")
  - **Password**: Any password (min 6 characters)
  - **Confirm Password**: Must match password
- Click **Register**
- ✅ You're registered! Redirected to dashboard

### 4. Login

- Go to **Login page**
- Enter:
  - **Email**: The email you registered with
  - **Password**: The password you used
- Click **Login**
- ✅ You're logged in! Access dashboard, chat, profile

---

## 📊 What's Working Now

### ✅ Authentication
- [x] User Registration with validation
- [x] User Login with password verification
- [x] JWT Token generation (30-minute expiry)
- [x] Protected routes (Chat, Dashboard, Profile require login)
- [x] Auto-logout on token expiry
- [x] Session persistence in localStorage

### ✅ Database
- [x] Mock in-memory database (no MongoDB needed)
- [x] Auto-fallback when MongoDB not configured
- [x] User data storage (name, email, password hash, role)
- [x] Chat history storage (ready for Phase 2)

### ✅ Frontend
- [x] Login page with error handling
- [x] Register page with password validation
- [x] Dashboard showing user greeting
- [x] Chat interface with subject selector
- [x] Profile page with logout
- [x] Navigation bar with logout button
- [x] Protected routes
- [x] Auto-redirect to login when not authenticated

---

## 🧪 Test Accounts

### Test Account 1
- **Email**: `test@example.com`
- **Password**: `password123`

### Test Account 2
- **Email**: `student@olmate.dev`
- **Password**: `learning123`

### Test Account 3
- **Email**: `admin@olmate.dev`
- **Password**: `admin@123`

> **Note**: Accounts are cleared when you restart the backend (in-memory database)

---

## 📁 File Changes

### New Files
- ✅ `backend/app/database/mock_db.py` - Mock database implementation
- ✅ `backend/test_auth.py` - Auth tests

### Modified Files
- ✅ `backend/app/database/mongodb.py` - Auto-fallback to mock DB
- ✅ `backend/app/auth/jwt_handler.py` - Improved password hashing
- ✅ `backend/main.py` - Database lifecycle events

---

## 🔄 How It Works

### Database Selection
1. **Startup**: Backend checks MongoDB URL
2. **If Valid URL**: Connects to MongoDB
3. **If Placeholder/Error**: Uses mock database
4. **User Sees**: No difference - API works same either way!

### Mock Database
- **Type**: In-memory (Python objects)
- **Storage**: Cleared on app restart
- **Speed**: Instant (no network calls)
- **Use Case**: Development/Testing

### Password Hashing
- **Algorithm**: Argon2 (best), fallback to SHA256
- **Security**: Good for development
- **Compatibility**: Works with older bcrypt versions

---

## 🔐 Credentials in LocalStorage

When you login, the app stores:
```javascript
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "5a5a3d7...",
    "name": "Test User",
    "email": "test@example.com",
    "role": "student"
  }
}
```

> **Note**: This is development setup. In production, use HTTPS + secure cookies

---

## 🚀 Next Steps

### Phase 2: OpenAI Integration
Once you have users logging in, you can:
1. Add real AI responses using OpenAI API
2. Replace placeholder chat responses
3. Store chat history in database
4. Implement streaming responses

### Production: Connect Real MongoDB
When ready for production:
1. Create MongoDB Atlas account (free tier available)
2. Get connection string
3. Set `MONGODB_URL` in `.env`
4. Restart backend
5. ✅ Automatically uses MongoDB instead of mock

---

## 🐛 Troubleshooting

### "Cannot read property 'token'"
- **Issue**: localStorage not syncing
- **Fix**: Hard refresh (Ctrl+F5) or clear browser cache

### "Invalid credentials"
- **Issue**: Wrong email or password
- **Fix**: Check Register page, use same email/password

### "Token expired"
- **Issue**: Token older than 30 minutes
- **Fix**: Login again (auto-logout redirects to login)

### Backend won't start
```bash
# Fix 1: Make sure Python installed
python --version

# Fix 2: Activate virtual environment
. .\venv\Scripts\Activate.ps1

# Fix 3: Install dependencies
pip install -r requirements.txt

# Fix 4: Run main.py
python main.py
```

### Frontend doesn't see backend
```bash
# In frontend .env, make sure:
VITE_API_URL=http://localhost:8001/api

# Frontend should show backend responses at:
# http://localhost:8000/api/health
```

---

## 📝 API Endpoints

### Authentication
| Method | Endpoint | Body |
|--------|----------|------|
| POST | `/api/auth/register` | `{name, email, password}` |
| POST | `/api/auth/login` | `{email, password}` |

### Chat (Requires Login Token)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat/send` | Send message to AI |
| GET | `/api/chat/history/{user_id}` | Get chat history |
| DELETE | `/api/chat/history/{chat_id}` | Delete single chat |

### Admin
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/users` | Get all users |
| POST | `/api/admin/documents/upload` | Upload PDF (Phase 3) |
| GET | `/api/admin/analytics` | Get usage stats (Phase 4) |

---

## 🎯 Testing Workflow

### Step 1: Run Backend Tests
```bash
cd backend
python test_auth.py
```

Should show: ✅ All auth tests passing

### Step 2: Manual Testing
1. Start backend: `python main.py`
2. Start frontend: `npm run dev`
3. Register new account
4. Login
5. Navigate to Chat
6. Send a question
7. View dashboard/profile

### Step 3: Check Swagger Docs
- Visit: **http://localhost:8000/docs**
- Try endpoints directly from browser
- See request/response schemas

---

## 📚 Documentation

- [README.md](../README.md) - Project overview
- [SETUP.md](../SETUP.md) - Full setup guide
- [COMPLETION.md](../COMPLETION.md) - Phase 1 status
- [GITHUB_SETUP.md](../GITHUB_SETUP.md) - GitHub workflow

---

## ✨ Summary

**Before**: ❌ Couldn't login/register (no MongoDB)
**After**: ✅ Login/register working with mock database

**Features Working**:
- ✅ Register new users
- ✅ Login with password verification
- ✅ JWT token auth
- ✅ Protected routes
- ✅ Session persistence
- ✅ Logout
- ✅ Chat interface
- ✅ Subject selection
- ✅ Profile page

**Ready for Phase 2**:
- ✅ User infrastructure complete
- ✅ Auth system tested
- ✅ Database ready (mock or real)
- ⏳ Next: OpenAI integration for real AI responses

---

**Questions?** Check the troubleshooting section or review test_auth.py for working examples!
