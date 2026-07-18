# OL Mate - AI-Powered Learning Assistant for Sri Lankan O/L Students

OL Mate is a full-stack AI-powered web application designed for Sri Lankan GCE Ordinary Level (O/L) students. It provides instant, syllabus-based academic assistance through a conversational chatbot powered by OpenAI GPT and Retrieval-Augmented Generation (RAG).

## 🎯 Features

### Student Features
- **User Authentication**: Secure registration and login with JWT
- **AI Chat Interface**: Ask questions and get instant responses
- **Subject Selection**: 14 O/L subjects supported
- **Chat History**: View and manage previous conversations
- **Responsive Design**: Mobile, tablet, and desktop friendly

### AI Features (Phase 2+)
- Syllabus-focused explanations
- Problem-solving assistance
- Past-paper practice
- Quiz generation
- Revision notes

### Admin Features (Phase 4)
- User management
- Document uploads (PDFs, notes, past papers)
- Analytics dashboard
- Content moderation

## 🏗️ Project Structure

```
ol-mate/
├── frontend/                # React 19 + TypeScript + Vite
│   ├── src/
│   │   ├── pages/          # DashboardPage, ChatPage, ProfilePage
│   │   ├── components/     # Reusable UI components
│   │   ├── services/       # API client & services
│   │   ├── contexts/       # Auth context
│   │   ├── utils/          # Constants & helpers
│   │   └── App.tsx         # Main app component
│   ├── package.json
│   └── vite.config.ts
├── backend/                # FastAPI + Python
│   ├── app/
│   │   ├── auth/           # JWT authentication
│   │   ├── routes/         # API endpoints
│   │   ├── models/         # Pydantic models
│   │   ├── database/       # MongoDB connection
│   │   ├── chatbot/        # OpenAI integration
│   │   └── rag/            # RAG implementation
│   ├── config.py           # Configuration
│   ├── main.py             # FastAPI app
│   ├── requirements.txt
│   └── .env.example
└── knowledge_base/         # RAG knowledge base

```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.12+
- MongoDB Atlas account
- OpenAI API key

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173`

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Update with your credentials

python main.py
```

Backend runs on `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

## 📚 O/L Subjects Supported

- Mathematics
- Science (Biology, Physics, Chemistry)
- English
- Sinhala
- Tamil
- History
- Buddhism
- Christianity
- Islam
- Hinduism
- ICT
- Commerce
- Geography
- Civic Education

## 🔐 Authentication

- JWT-based authentication
- Bcrypt password hashing
- Secure token storage
- Auto-logout on token expiration

## 💾 Database

**MongoDB Collections:**
- `users` - Student and admin profiles
- `chats` - Conversation history
- `documents` - Uploaded study materials

## 🤖 AI Integration

- **LLM**: OpenAI GPT-4 / GPT-5
- **RAG**: ChromaDB for embeddings
- **Framework**: LangChain for orchestration

## 📋 Development Phases

### Phase 1: Core App ✓
- Authentication (Register, Login)
- Dashboard
- Chat UI
- Subject selector
- Responsive layout

### Phase 2: AI Features (In Progress)
- OpenAI API integration
- Chat history persistence
- Streaming responses
- Feedback system

### Phase 3: Knowledge Base
- PDF upload & processing
- ChromaDB embeddings
- RAG context retrieval
- Syllabus-grounded answers

### Phase 4: Admin & Analytics
- Admin dashboard
- User management
- Document management
- Usage analytics

## 🛠️ Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, TypeScript, Vite, Tailwind CSS, shadcn/ui |
| Backend | FastAPI, Python 3.12, Uvicorn |
| Database | MongoDB Atlas |
| AI/ML | OpenAI GPT, ChromaDB, LangChain |
| Auth | JWT, Bcrypt |
| Deployment | Vercel (Frontend), Render (Backend) |

## 📖 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user

### Chat
- `POST /api/chat/send` - Send message to AI
- `GET /api/chat/history/{user_id}` - Get chat history
- `DELETE /api/chat/history/{chat_id}` - Delete chat

### Admin
- `GET /api/admin/users` - List users
- `POST /api/admin/documents/upload` - Upload study material
- `GET /api/admin/analytics` - Get usage analytics

## 🎓 Sample AI Prompts

Students can ask:
- "Explain photosynthesis for O/L"
- "Solve this quadratic equation"
- "What are the causes of World War I?"
- "Give me a summary of electricity"
- "Create 5 MCQs from acids and bases"

## 📝 Environment Variables

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000/api
```

### Backend (.env)
```
MONGODB_URL=mongodb+srv://user:password@cluster.mongodb.net/olmate
DATABASE_NAME=olmate
SECRET_KEY=your-secret-key
OPENAI_API_KEY=sk-your-openai-key
CHROMA_DB_PATH=./chroma_data
```

## 🤝 Contributing

1. Create a feature branch (`git checkout -b feature/amazing-feature`)
2. Commit changes (`git commit -m 'Add amazing feature'`)
3. Push to branch (`git push origin feature/amazing-feature`)
4. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Author

Created as a Final Year Project for Sri Lankan GCE Ordinary Level Education.

## 🙏 Acknowledgments

- Sri Lankan O/L Syllabus & Curriculum
- OpenAI for GPT API
- FastAPI & React communities

---

**OL Mate** - Making O/L exam preparation smarter, faster, and more accessible! 📚✨
