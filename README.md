# OL Mate

OL Mate is a full-stack study web app for Sri Lankan GCE Ordinary Level
students. It includes authentication, a realtime AI tutor, saved chat history,
knowledge-base retrieval, quiz generation, scoring, and admin document upload.

## What Works Now

- Student registration and login with JWT.
- Responsive dashboard, profile, chat, and quiz pages.
- Realtime ChatGPT-style streaming answers.
- O/L subject selection across 14 app subjects.
- Saved chat history with delete support.
- Knowledge-base retrieval from `.md`, `.txt`, and `.pdf` files.
- Starter knowledge pack in `knowledge_base/`.
- Quiz generation, answer submission, scoring, and explanations.
- Admin user listing, document upload/listing, and analytics.
- MongoDB support with local in-memory fallback for development.

## Tech Stack

| Layer | Technology |
| --- | --- |
| Frontend | React, TypeScript, Vite, Tailwind CSS |
| Backend | FastAPI, Python, Uvicorn |
| Database | MongoDB Atlas or local in-memory development database |
| AI | OpenAI API when configured, local tutor fallback otherwise |
| Knowledge | Local file retrieval from `knowledge_base/` |

## Project Structure

```text
OLmate/
  backend/
    app/
      auth/
      chatbot/
      database/
      models/
      rag/
      routes/
    main.py
    config.py
    requirements.txt
  frontend/
    src/
      contexts/
      pages/
      services/
      utils/
    package.json
  knowledge_base/
    mathematics.md
    science.md
    english.md
    ...
```

## Local Setup

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python main.py
```

Backend:
`http://localhost:8000`

API docs:
`http://localhost:8000/docs`

If port `8000` is already busy during local development, `python main.py` and
`python run_dev.py` automatically use the next free port. To force a specific
port in PowerShell:

```powershell
$env:PORT=8001
python main.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend:
`http://localhost:5173`

## Environment Variables

Frontend `.env`:

```env
VITE_API_URL=http://localhost:8001/api
```

Backend `.env`:

```env
MONGODB_URL=mongodb+srv://user:password@cluster.mongodb.net/olmate
DATABASE_NAME=olmate
SECRET_KEY=change-this-to-a-long-random-secret
OPENAI_API_KEY=sk-your-openai-api-key
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,https://your-frontend-domain.com
KNOWLEDGE_BASE_PATH=../knowledge_base
```

`OPENAI_API_KEY` is optional for development. If it is missing, OL Mate uses a
local deterministic tutor so the app remains usable.

## Knowledge Base

The app reads files from `knowledge_base/` automatically.

Supported file types:
- `.md`
- `.txt`
- `.pdf`

Add subject notes, textbook summaries, teacher notes, or original revision
material there. The chat bot and quiz generator will retrieve relevant chunks
from those files.

The repository includes a starter pack for:
- Mathematics
- Science
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

## Main API Endpoints

Authentication:
- `POST /api/auth/register`
- `POST /api/auth/login`

Chat:
- `POST /api/chat/send`
- `POST /api/chat/stream`
- `GET /api/chat/history/{user_id}`
- `DELETE /api/chat/history/{chat_id}`

Quiz:
- `POST /api/quiz/generate`
- `POST /api/quiz/{quiz_id}/submit`
- `GET /api/quiz/history/{user_id}`

Admin:
- `GET /api/admin/users`
- `POST /api/admin/documents/upload`
- `GET /api/admin/documents`
- `GET /api/admin/analytics`

## Build And Test

Frontend production build:

```bash
cd frontend
npm run build
```

Backend checks:

```bash
cd backend
python -m compileall app main.py
python test_auth.py
```

## Deployment Notes

Frontend can be deployed to Vercel, Netlify, or any static host using
`npm run build`.

Backend can be deployed to Render, Railway, Fly.io, or another Python host.
Use this start command from the `backend` directory:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

For production:
- Set a real `SECRET_KEY`.
- Set `MONGODB_URL` to MongoDB Atlas or another reachable MongoDB instance.
- Set `CORS_ORIGINS` to the real frontend domain.
- Add `OPENAI_API_KEY` for live AI responses.
- Keep `knowledge_base/` available to the backend process or set
  `KNOWLEDGE_BASE_PATH` to the deployed content path.

## License

MIT
