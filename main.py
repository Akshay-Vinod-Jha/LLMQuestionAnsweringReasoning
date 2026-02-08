"""
FastAPI Application: Auto Test Generator & Evaluator
Feature-9 for AI-Powered Multimodal Smart Learning Assistant
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

# Import routes
from routes_generate import router as generate_router
from routes_evaluate import router as evaluate_router


# Load environment variables
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown"""
    # Startup
    print("🚀 Auto Test Generator & Evaluator starting...")
    
    # Verify Groq API key
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("⚠️  WARNING: GROQ_API_KEY not found in environment!")
        print("   Set it in .env file or environment variables")
    else:
        print("✓ Groq API key configured")
    
    print("✓ Application ready")
    
    yield
    
    # Shutdown
    print("👋 Application shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Auto Test Generator & Evaluator API",
    description="AI-powered test generation and evaluation system using Groq Cloud API",
    version="1.0.0",
    lifespan=lifespan
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(generate_router)
app.include_router(evaluate_router)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Auto Test Generator & Evaluator",
        "version": "1.0.0",
        "endpoints": {
            "generate": "/test/generate",
            "evaluate": "/test/evaluate"
        }
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    api_key_configured = bool(os.getenv("GROQ_API_KEY"))
    
    return {
        "status": "healthy" if api_key_configured else "degraded",
        "groq_api_configured": api_key_configured,
        "models": {
            "generation": "llama-3.1-8b-instant",
            "evaluation": "llama-3.1-8b-instant"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment or default to 8000
    port = int(os.getenv("PORT", "8000"))
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
