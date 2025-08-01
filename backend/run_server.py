#!/usr/bin/env python3
"""
Simple server runner for the Programming Problem Platform
"""

import sys
from pathlib import Path

# Add backend to Python path
backend_root = Path(__file__).parent
sys.path.insert(0, str(backend_root))
sys.path.insert(0, str(backend_root / "pkgs" / "auth"))
sys.path.insert(0, str(backend_root / "pkgs" / "problem-system"))
sys.path.insert(0, str(backend_root / "pkgs" / "judge-system"))
sys.path.insert(0, str(backend_root / "pkgs" / "core"))
sys.path.insert(0, str(backend_root / "pkgs" / "seed"))

if __name__ == "__main__":
    import uvicorn
    from src.main import app
    
    print("🚀 Starting Programming Problem Platform...")
    print("📊 Available endpoints:")
    print("  - API Documentation: http://localhost:8901/docs")
    print("  - Health Check: http://localhost:8901/health")
    print("  - API Test Page: http://localhost:3000/api-test")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8901,
        reload=False,  # Disable reload to avoid import issues
        log_level="info"
    )