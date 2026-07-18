# OL Mate - AI-Powered Learning Assistant for Sri Lankan O/L Students

## Project Overview
OL Mate is a full-stack AI-powered web application that provides Sri Lankan GCE Ordinary Level students with instant, syllabus-based academic assistance through a conversational chatbot.

## Technology Stack
- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS, shadcn/ui, React Router, TanStack Query, Axios
- **Backend**: FastAPI, Python 3.12, MongoDB Atlas, JWT Authentication, Pydantic, Uvicorn
- **AI/ML**: OpenAI GPT API, ChromaDB, LangChain, RAG
- **Deployment**: Vercel (frontend), Render (backend)

## Development Checklist

- [x] Verify copilot-instructions.md file created
- [x] Clarify Project Requirements
- [x] Scaffold Frontend Project (React + Vite + TypeScript)
- [x] Scaffold Backend Project (FastAPI + Python)
- [x] Set up Authentication System (JWT)
- [x] Build ChatGPT-Style Interface
- [ ] Integrate OpenAI API (Phase 2)
- [ ] Implement RAG Knowledge Base (Phase 3)
- [ ] Create Quiz Generator (Phase 2+)
- [ ] Build Admin Dashboard (Phase 4)
- [ ] Add AI Study Tools (Phase 2+)
- [x] Compile and Test
- [x] Create and Run Tasks
- [x] Documentation Complete

## Key Features
1. **Student Features**: Register/Login, Ask Questions, Subject Selection, Chat History, Quizzes, Revision Notes
2. **AI Features**: Syllabus-focused explanations, Problem solving, Study materials
3. **Admin Features**: User management, Document uploads, Analytics, Content moderation

## Project Structure
```
ol-mate/
├── .github/
│   └── copilot-instructions.md
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── layouts/
│   │   ├── services/
│   │   ├── contexts/
│   │   └── utils/
│   └── package.json
├── backend/
│   ├── app/
│   │   ├── auth/
│   │   ├── chatbot/
│   │   ├── rag/
│   │   ├── routes/
│   │   ├── models/
│   │   ├── database/
│   │   └── services/
│   └── requirements.txt
├── knowledge_base/
└── README.md
```

## Development Phases
- **Phase 1**: Core app (Authentication, Dashboard, Chat UI, Subject Selector)
- **Phase 2**: AI features (LLM integration, Chat History, Streaming Responses)
- **Phase 3**: Knowledge Base (PDF Upload, ChromaDB, RAG)
- **Phase 4**: Admin & Analytics (Admin Dashboard, Usage Analytics, Document Management)
