from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import logging.handlers
import os
from config import settings
from app.database.mongodb import MongoDatabase
from app.server import parse_port, select_available_port

# Configure basic logging for the application
log_dir = os.path.dirname(settings.LOG_FILE)
if log_dir and not os.path.exists(log_dir):
    try:
        os.makedirs(log_dir, exist_ok=True)
    except Exception:
        pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.handlers.RotatingFileHandler(settings.LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3),
    ],
)
logger = logging.getLogger("olmate")

if settings.SECRET_KEY == "your-secret-key-change-in-production":
    logger.warning("Using default SECRET_KEY — change this in production!")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and close database resources with the app lifecycle."""
    MongoDatabase.connect_db()
    print(f"[OK] OL Mate API v{settings.APP_VERSION} started")
    yield
    MongoDatabase.close_db()
    print("[OK] OL Mate API stopped")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered learning assistant for Sri Lankan O/L students",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "app": settings.APP_NAME}

# Import routes
from app.routes import auth, chat, admin, quiz

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(quiz.router, prefix="/api/quiz", tags=["quiz"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    requested_port = parse_port(os.getenv("PORT"))
    port = requested_port

    if "PORT" not in os.environ:
        port = select_available_port(host, requested_port)
        if port != requested_port:
            print(
                f"[WARNING] Port {requested_port} is already in use; "
                f"starting OL Mate API on port {port} instead"
            )

    uvicorn.run(app, host=host, port=port)
