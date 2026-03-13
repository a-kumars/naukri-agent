#!/usr/bin/env python3
"""
Quick setup verification script for Naukri Agent
Run this after updating your .env file with real credentials
"""

import os
import sys
from dotenv import load_dotenv

def main():
    print("🔍 Naukri Agent Setup Verification")
    print("=" * 40)

    # Load environment variables
    load_dotenv()

    # Check .env file
    env_file = ".env"
    if os.path.exists(env_file):
        print("✅ .env file exists")
    else:
        print("❌ .env file missing - copy from .env.example")
        return False

    # Check credentials
    email = os.getenv("NAUKRI_EMAIL")
    password = os.getenv("NAUKRI_PASSWORD")

    if email and email != "your_email@example.com":
        print("✅ Email configured")
    else:
        print("❌ Email not configured in .env")
        return False

    if password and password != "your_password":
        print("✅ Password configured")
    else:
        print("❌ Password not configured in .env")
        return False

    # Check resume file
    import config
    if os.path.exists(config.RESUME_FILE_PATH):
        print(f"✅ Resume file found: {config.RESUME_FILE_PATH}")
    else:
        print(f"❌ Resume file missing: {config.RESUME_FILE_PATH}")
        return False

    # Check data directory
    if os.path.exists("data"):
        print("✅ Data directory exists")
    else:
        print("❌ Data directory missing")
        os.makedirs("data", exist_ok=True)
        print("📁 Created data directory")

    # Check logs directory
    if os.path.exists("logs"):
        print("✅ Logs directory exists")
    else:
        print("❌ Logs directory missing")
        os.makedirs("logs", exist_ok=True)
        print("📁 Created logs directory")

    print("\n🎉 Setup verification complete!")
    print("🚀 Ready to run: python main.py")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)