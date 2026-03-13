#!/usr/bin/env python3
"""
Git Setup Script for Naukri Agent
Run this to configure Git and prepare for publishing
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=os.getcwd())
        if result.returncode == 0:
            print(f"✅ {description}")
            return True
        else:
            print(f"❌ {description}: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description}: {str(e)}")
        return False

def main():
    print("🚀 Git Setup for Naukri Agent")
    print("=" * 40)

    # Check if Git is available
    if not run_command("git --version", "Git installation check"):
        print("❌ Git is not installed. Please install Git first.")
        return False

    # Check current Git config
    name_result = subprocess.run("git config --global user.name", shell=True, capture_output=True, text=True)
    email_result = subprocess.run("git config --global user.email", shell=True, capture_output=True, text=True)

    if name_result.returncode == 0 and email_result.returncode == 0:
        name = name_result.stdout.strip()
        email = email_result.stdout.strip()
        print(f"✅ Git already configured: {name} <{email}>")
    else:
        print("⚠️  Git not configured. Please run these commands:")
        print()
        print("git config --global user.name \"Your Full Name\"")
        print("git config --global user.email \"your.email@github.com\"")
        print()
        print("Replace with your actual name and GitHub email address.")
        return False

    # Initialize repository if not already done
    if not os.path.exists(".git"):
        if not run_command("git init", "Initialize Git repository"):
            return False

    # Create .gitignore
    gitignore_content = """# Environment variables
.env
.env.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
logs/
*.log

# Data files (optional - uncomment if you want to ignore)
# data/
# resume/
"""

    with open(".gitignore", "w") as f:
        f.write(gitignore_content)
    print("✅ Created .gitignore file")

    # Add all files
    if not run_command("git add .", "Add all files to Git"):
        return False

    # Initial commit
    if not run_command('git commit -m "Initial commit: Naukri Agent automation project"', "Create initial commit"):
        return False

    print()
    print("🎉 Git repository setup complete!")
    print()
    print("📝 Next steps:")
    print("1. Create a new repository on GitHub.com")
    print("2. Copy the repository URL")
    print("3. Run: git remote add origin <your-repo-url>")
    print("4. Run: git push -u origin main")
    print()
    print("Need help with GitHub repository creation?")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)