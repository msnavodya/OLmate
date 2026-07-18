from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from app.database.mongodb import MongoDatabase

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered learning assistant for Sri Lankan O/L students"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database lifecycle events
@app.on_event("startup")
async def startup_event():
    """Initialize database connection on app startup"""
    MongoDatabase.connect_db()
    print(f"[OK] OL Mate API v{settings.APP_VERSION} started")

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on app shutdown"""
    MongoDatabase.close_db()
    print("[OK] OL Mate API stopped")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "app": settings.APP_NAME}

# Import routes
from app.routes import auth, chat, admin

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
