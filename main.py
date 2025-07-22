"""
FastAPI E-commerce Microservice - Production Ready (API Only)
Optimized for Render deployment with no frontend dependencies
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from db import connect_to_mongo, close_mongo_connection
from routers import products, orders

# Production logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]  # Console output for Render logs
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup and shutdown events."""
    try:
        logger.info("🚀 Starting FastAPI E-commerce Microservice")
        logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
        logger.info(f"Port: {os.getenv('PORT', 8000)}")
        
        await connect_to_mongo()
        logger.info("✅ Database connection established")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {str(e)}")
        raise
    finally:
        logger.info("🔄 Shutting down application")
        await close_mongo_connection()
        logger.info("✅ Application shutdown complete")

# Initialize FastAPI app
app = FastAPI(
    title="E-commerce Microservice API",
    description="Production-ready FastAPI e-commerce backend for products and orders management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS configuration - optimized for API-only deployment
# Since you're not serving a frontend, this allows external API access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for API access
    allow_credentials=False,  # Not needed for API-only
    allow_methods=["GET", "POST"],  # Only methods you actually use
    allow_headers=["*"],
)

# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "status_code": 500}
    )

# Health check endpoint (required for Render)
@app.get("/health")
async def health_check():
    """Health check endpoint for Render deployment monitoring"""
    return {
        "status": "healthy",
        "service": "ecommerce-api",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "unknown")
    }

# Root endpoint with API information
@app.get("/")
async def root():
    """Root endpoint with API documentation links"""
    base_url = f"https://{os.getenv('RENDER_SERVICE_NAME', 'localhost')}.onrender.com" if os.getenv('RENDER_SERVICE_NAME') else "http://localhost:8000"
    
    return {
        "message": "FastAPI E-commerce Microservice API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "documentation": f"{base_url}/docs",
            "health": f"{base_url}/health",
            "products": f"{base_url}/products",
            "orders": f"{base_url}/orders/{{user_id}}"
        },
        "environment": os.getenv("ENVIRONMENT", "unknown")
    }

# Include routers (no versioning needed for simple API-only deployment)
app.include_router(products.router, tags=["Products"])
app.include_router(orders.router, tags=["Orders"])

if __name__ == "__main__":
    import uvicorn
    
    # Production server configuration for Render
    port = int(os.getenv("PORT", 8000))
    host = "0.0.0.0"  # Required for Render
    
    logger.info(f"🌐 Starting server on {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        log_level="info",
        access_log=True,
        reload=False,  # Always False in production
        workers=1      # Single worker for free tier
    )
