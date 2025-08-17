#!/usr/bin/env python3
"""
Quick test script to verify Supabase connection
"""
import os
import sys
sys.path.append('.')

from ppcore.infrastructure.supabase.client import create_client
from ppcore.domain.protocols.database_protocols import DatabaseConfig

def test_connection():
    """Test basic Supabase connection"""
    
    # Load environment variables
    supabase_url = os.getenv("SUPABASE_URL", "http://localhost:54221")
    supabase_key = os.getenv("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0")
    
    print(f"Testing connection to: {supabase_url}")
    print(f"Using key: {supabase_key[:20]}...")
    
    # Create config and client
    config = DatabaseConfig(url=supabase_url, key=supabase_key)
    client = create_client(config)
    
    try:
        # Try a simple query
        result = client.table("books").select("*").execute()
        print(f"Connection successful! Found {len(result.data)} books")
        return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

if __name__ == "__main__":
    # Set environment variables from .env file
    env_file = "/mnt/d/nodashin/python-problem/backend/.env"
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
    
    success = test_connection()
    sys.exit(0 if success else 1)