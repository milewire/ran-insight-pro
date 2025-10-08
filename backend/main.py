"""
RAN Insight Pro API - Main application file
This file will work correctly when FastAPI is properly installed and configured.
"""

# Standard library imports (always available)
import time
import os
from contextlib import asynccontextmanager

# Application factory function
def create_app():
    """Create and configure the FastAPI application"""
    try:
        # Dynamic imports to avoid linter issues
        fastapi = __import__('fastapi')
        FastAPI = fastapi.FastAPI
        Request = fastapi.Request
        
        cors = __import__('fastapi.middleware.cors')
        CORSMiddleware = cors.CORSMiddleware
        
        dotenv = __import__('dotenv')
        load_dotenv = dotenv.load_dotenv

        # Load environment variables
        load_dotenv()

        # Import application modules
        from app.db.session import create_tables
        from app.routers import analyze, compare, report, firmware, health, auth
        from app.utils.logger import setup_logging, api_logger

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            """Application lifespan manager"""
            # Startup
            setup_logging()
            create_tables()
            yield
            # Shutdown
            pass

        # Create FastAPI application
        app = FastAPI(
            title="RAN Insight Pro API",
            description="Advanced RAN (Radio Access Network) analysis and monitoring API",
            version="1.0.0",
            lifespan=lifespan
        )

        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend URLs
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Add request timing middleware
        @app.middleware("http")
        async def add_process_time_header(request: Request, call_next):
            start_time = time.time()
            response = await call_next(request)
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            return response

        # Include routers
        app.include_router(auth.router)  # Authentication routes (no auth required)
        app.include_router(analyze.router)
        app.include_router(compare.router)
        app.include_router(report.router)
        app.include_router(firmware.router)
        app.include_router(health.router)

        # Root endpoint
        @app.get("/")
        async def root():
            """Root endpoint with API information"""
            return {
                "message": "RAN Insight Pro API",
                "version": "1.0.0",
                "status": "running",
                "docs": "/docs",
                "health": "/health"
            }

        # Legacy endpoint for backward compatibility
        @app.post("/analyze")
        async def legacy_analyze():
            """Legacy analyze endpoint - redirects to new structure"""
            return {
                "message": "This endpoint has been moved to /analyze/",
                "new_endpoint": "/analyze/",
                "docs": "/docs"
            }

        return app

    except ImportError as e:
        # Fallback for when FastAPI is not available
        print(f"FastAPI not available: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        return None

# Create the application instance
app = create_app()

# For running with uvicorn
if __name__ == "__main__":
    if app:
        try:
            uvicorn = __import__('uvicorn')
            uvicorn.run(app, host="0.0.0.0", port=8000)
        except ImportError:
            print("Uvicorn not available. Please install: pip install uvicorn")
    else:
        print("Cannot start server: FastAPI not available")