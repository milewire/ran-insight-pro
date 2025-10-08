#!/usr/bin/env python3
"""
RAN Insight Pro Backend Server - Simple Startup
This script starts the server without reload mode to avoid multiprocessing issues
"""

import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    
    print(f"🚀 Starting RAN Insight Pro API server...")
    print(f"📍 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"📊 Log Level: {log_level}")
    print(f"📚 API Documentation: http://{host}:{port}/docs")
    print(f"❤️  Health Check: http://{host}:{port}/health")
    print(f"🔍 Simple Health: http://{host}:{port}/health/simple")
    print("\n" + "="*50)
    print("Press CTRL+C to stop the server")
    print("="*50 + "\n")
    
    try:
        # Start the server without reload to avoid multiprocessing issues
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=False,  # Disable reload to avoid multiprocessing issues
            log_level=log_level,
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        print("💡 Try running: python setup.py")
