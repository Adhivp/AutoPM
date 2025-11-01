#!/usr/bin/env python3
"""
Quick Setup Script for AI Chat & Vector Search
Validates environment and initializes the system
"""
import os
import sys
from pathlib import Path


def check_environment():
    """Check if all required environment variables are set"""
    print("🔍 Checking environment variables...")
    
    required_vars = {
        'DATABASE_URL': 'Database connection string',
        'JWT_SECRET': 'JWT secret key',
        'ENCRYPTION_KEY': 'Token encryption key',
        'GEMINI_API_KEY': 'Google Gemini API key (NEW!)',
        'GITHUB_CLIENT_ID': 'GitHub OAuth client ID',
        'GITHUB_CLIENT_SECRET': 'GitHub OAuth secret',
        'JIRA_CLIENT_ID': 'Jira OAuth client ID',
        'JIRA_CLIENT_SECRET': 'Jira OAuth secret'
    }
    
    missing = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing.append(f"  ❌ {var}: {description}")
            print(f"  ❌ {var}")
        else:
            print(f"  ✅ {var}")
    
    if missing:
        print("\n⚠️  Missing required environment variables:")
        for item in missing:
            print(item)
        print("\nPlease add these to your .env file")
        return False
    
    print("✅ All required environment variables are set!\n")
    return True


def check_dependencies():
    """Check if required Python packages are installed"""
    print("🔍 Checking Python dependencies...")
    
    required_packages = {
        'fastapi': 'FastAPI framework',
        'google.genai': 'Google Gemini SDK',
        'chromadb': 'Vector database',
        'sqlalchemy': 'Database ORM',
        'numpy': 'Numerical computing'
    }
    
    missing = []
    for package, description in required_packages.items():
        try:
            __import__(package.replace('.', '/'))
            print(f"  ✅ {package}")
        except ImportError:
            missing.append(f"  ❌ {package}: {description}")
            print(f"  ❌ {package}")
    
    if missing:
        print("\n⚠️  Missing required packages:")
        for item in missing:
            print(item)
        print("\nRun: pip install -r requirements.txt")
        return False
    
    print("✅ All required packages are installed!\n")
    return True


def check_database():
    """Check database connection"""
    print("🔍 Checking database connection...")
    
    try:
        from database import engine
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print("  ✅ Database connection successful\n")
            return True
    except Exception as e:
        print(f"  ❌ Database connection failed: {str(e)}\n")
        return False


def check_tables():
    """Check if required tables exist"""
    print("🔍 Checking database tables...")
    
    required_tables = [
        'github_comments',
        'jira_comments',
        'sync_logs',
        'vector_embeddings',
        'chat_history'
    ]
    
    try:
        from database import engine
        from sqlalchemy import inspect
        
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        missing = []
        for table in required_tables:
            if table in existing_tables:
                print(f"  ✅ {table}")
            else:
                missing.append(table)
                print(f"  ❌ {table}")
        
        if missing:
            print(f"\n⚠️  Missing tables: {', '.join(missing)}")
            print("Run: python scripts/migrate_sync_tables.py")
            return False
        
        print("✅ All required tables exist!\n")
        return True
        
    except Exception as e:
        print(f"  ❌ Error checking tables: {str(e)}\n")
        return False


def test_gemini_api():
    """Test Gemini API connection"""
    print("🔍 Testing Google Gemini API...")
    
    try:
        from google import genai
        
        client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
        
        # Test embedding
        result = client.models.embed_content(
            model="models/text-embedding-004",
            content="test"
        )
        
        if result.embeddings and len(result.embeddings[0].values) > 0:
            print(f"  ✅ Embedding API working (dimensions: {len(result.embeddings[0].values)})")
        else:
            print("  ❌ Embedding API returned empty result")
            return False
        
        # Test chat
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Say 'API test successful' and nothing else."
        )
        
        if response.text:
            print("  ✅ Chat API working")
            print("✅ Gemini API is operational!\n")
            return True
        else:
            print("  ❌ Chat API returned empty result")
            return False
            
    except Exception as e:
        print(f"  ❌ Gemini API test failed: {str(e)}")
        print("  Check your GEMINI_API_KEY\n")
        return False


def check_chromadb():
    """Check ChromaDB setup"""
    print("🔍 Checking ChromaDB...")
    
    try:
        import chromadb
        from chromadb.config import Settings
        
        client = chromadb.PersistentClient(
            path="./chroma_db",
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Try to create a test collection
        collection = client.get_or_create_collection("test_collection")
        print(f"  ✅ ChromaDB initialized")
        print(f"  📁 Storage location: ./chroma_db/")
        print("✅ ChromaDB is ready!\n")
        return True
        
    except Exception as e:
        print(f"  ❌ ChromaDB check failed: {str(e)}\n")
        return False


def print_summary(checks):
    """Print summary of all checks"""
    print("\n" + "="*60)
    print("SETUP SUMMARY")
    print("="*60)
    
    all_passed = all(checks.values())
    
    for check_name, passed in checks.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {check_name}")
    
    print("="*60)
    
    if all_passed:
        print("\n🎉 All checks passed! Your system is ready!")
        print("\nNext steps:")
        print("1. Start the server: python3 main.py")
        print("2. Trigger a sync: POST /api/sync/trigger")
        print("3. Generate embeddings: POST /api/ai/embeddings/generate-all")
        print("4. Start chatting: POST /api/ai/chat")
        print("\n📚 See AI_CHAT_GUIDE.md for detailed usage")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("📚 See AI_CHAT_GUIDE.md for setup instructions")
    
    print()


def main():
    """Run all checks"""
    print("\n" + "="*60)
    print("AutoPM AI Chat & Vector Search Setup Validator")
    print("="*60 + "\n")
    
    checks = {
        "Environment Variables": check_environment(),
        "Python Dependencies": check_dependencies(),
        "Database Connection": check_database(),
        "Database Tables": check_tables(),
        "Google Gemini API": test_gemini_api(),
        "ChromaDB": check_chromadb()
    }
    
    print_summary(checks)
    
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    # Change to script directory
    os.chdir(Path(__file__).parent.parent)
    sys.exit(main())
