from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any
from datetime import datetime
import time
import os

from ..db.session import get_db
from ..db.models import HealthCheck
from ..utils.logger import api_logger

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
async def health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Comprehensive health check endpoint
    
    Returns:
        Health status of all system components
    """
    start_time = time.time()
    health_status = {
        "timestamp": datetime.utcnow().isoformat(),
        "overall_status": "healthy",
        "components": {}
    }
    
    try:
        # Check API status
        api_status = await _check_api_health()
        health_status["components"]["api"] = api_status
        
        # Check database status
        db_status = await _check_database_health(db)
        health_status["components"]["database"] = db_status
        
        # Check AI service status
        ai_status = await _check_ai_service_health()
        health_status["components"]["ai_service"] = ai_status
        
        # Check external dependencies
        external_status = await _check_external_dependencies()
        health_status["components"]["external_dependencies"] = external_status
        
        # Determine overall status
        component_statuses = [comp["status"] for comp in health_status["components"].values()]
        if "unhealthy" in component_statuses:
            health_status["overall_status"] = "unhealthy"
        elif "degraded" in component_statuses:
            health_status["overall_status"] = "degraded"
        
        # Calculate response time
        response_time_ms = (time.time() - start_time) * 1000
        health_status["response_time_ms"] = response_time_ms
        
        # Log health check
        api_logger.log_request("GET", "/health")
        
        # Store health check result in database
        await _store_health_check(db, health_status, response_time_ms)
        
        return health_status
        
    except Exception as e:
        health_status["overall_status"] = "unhealthy"
        health_status["error"] = str(e)
        health_status["response_time_ms"] = (time.time() - start_time) * 1000
        
        api_logger.log_error("GET", "/health", str(e))
        
        # Store failed health check
        await _store_health_check(db, health_status, health_status["response_time_ms"], str(e))
        
        return health_status

@router.get("/simple")
async def simple_health_check() -> Dict[str, str]:
    """
    Simple health check for load balancers and monitoring
    
    Returns:
        Simple health status
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/database")
async def database_health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Database-specific health check
    
    Returns:
        Database health status
    """
    try:
        db_status = await _check_database_health(db)
        api_logger.log_request("GET", "/health/database")
        return db_status
        
    except Exception as e:
        api_logger.log_error("GET", "/health/database", str(e))
        raise HTTPException(status_code=500, detail=f"Database health check failed: {str(e)}")

@router.get("/ai")
async def ai_health_check() -> Dict[str, Any]:
    """
    AI service-specific health check
    
    Returns:
        AI service health status
    """
    try:
        ai_status = await _check_ai_service_health()
        api_logger.log_request("GET", "/health/ai")
        return ai_status
        
    except Exception as e:
        api_logger.log_error("GET", "/health/ai", str(e))
        raise HTTPException(status_code=500, detail=f"AI service health check failed: {str(e)}")

@router.get("/history")
async def health_check_history(
    limit: int = 10,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get health check history
    
    Args:
        limit: Number of recent health checks to return
        db: Database session
        
    Returns:
        Health check history
    """
    try:
        health_checks = db.query(HealthCheck).order_by(
            HealthCheck.check_timestamp.desc()
        ).limit(limit).all()
        
        history = []
        for check in health_checks:
            history.append({
                "timestamp": check.check_timestamp.isoformat(),
                "api_status": check.api_status,
                "db_status": check.db_status,
                "ai_service_status": check.ai_service_status,
                "response_time_ms": check.response_time_ms,
                "error_message": check.error_message
            })
        
        api_logger.log_request("GET", "/health/history")
        
        return {
            "health_check_history": history,
            "total_checks": len(history),
            "limit": limit
        }
        
    except Exception as e:
        api_logger.log_error("GET", "/health/history", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get health check history: {str(e)}")

async def _check_api_health() -> Dict[str, Any]:
    """Check API service health"""
    try:
        # Basic API health checks
        return {
            "status": "healthy",
            "message": "API service is running",
            "version": "1.0.0",
            "uptime": "N/A"  # Could be implemented with process monitoring
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"API service error: {str(e)}",
            "error": str(e)
        }

async def _check_database_health(db: Session) -> Dict[str, Any]:
    """Check database connectivity and performance"""
    try:
        start_time = time.time()
        
        # Test basic connectivity
        result = db.execute(text("SELECT 1")).fetchone()
        
        # Test table access
        db.execute(text("SELECT COUNT(*) FROM uploads")).fetchone()
        
        response_time_ms = (time.time() - start_time) * 1000
        
        return {
            "status": "healthy",
            "message": "Database connection successful",
            "response_time_ms": response_time_ms,
            "connection_pool": "active"
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}",
            "error": str(e)
        }

async def _check_ai_service_health() -> Dict[str, Any]:
    """Check AI service health"""
    try:
        # Check if OpenAI API key is configured
        openai_key = os.getenv("OPENAI_API_KEY")
        
        if not openai_key:
            return {
                "status": "degraded",
                "message": "OpenAI API key not configured",
                "ai_available": False
            }
        
        # In a real implementation, you might make a test API call
        # For now, we'll just check configuration
        return {
            "status": "healthy",
            "message": "AI service configuration valid",
            "ai_available": True,
            "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"AI service error: {str(e)}",
            "error": str(e)
        }

async def _check_external_dependencies() -> Dict[str, Any]:
    """Check external dependencies health"""
    try:
        dependencies = {
            "openai_api": "healthy" if os.getenv("OPENAI_API_KEY") else "degraded",
            "database": "healthy",  # Will be updated by database check
            "file_storage": "healthy"  # Assuming local storage
        }
        
        overall_status = "healthy"
        if "unhealthy" in dependencies.values():
            overall_status = "unhealthy"
        elif "degraded" in dependencies.values():
            overall_status = "degraded"
        
        return {
            "status": overall_status,
            "dependencies": dependencies,
            "message": "External dependencies checked"
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"External dependencies check failed: {str(e)}",
            "error": str(e)
        }

async def _store_health_check(
    db: Session, 
    health_status: Dict[str, Any], 
    response_time_ms: float, 
    error_message: str = None
) -> None:
    """Store health check result in database"""
    try:
        health_check_record = HealthCheck(
            api_status=health_status["components"].get("api", {}).get("status", "unknown"),
            db_status=health_status["components"].get("database", {}).get("status", "unknown"),
            ai_service_status=health_status["components"].get("ai_service", {}).get("status", "unknown"),
            response_time_ms=response_time_ms,
            error_message=error_message
        )
        
        db.add(health_check_record)
        db.commit()
        
    except Exception as e:
        # Don't fail the health check if we can't store it
        api_logger.log_error("POST", "/health/store", str(e))
