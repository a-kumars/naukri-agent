#!/usr/bin/env python3
"""
GitHub Connection Script for Naukri Agent
Run this after creating your GitHub repository
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and return success status"""
    try:
        print(f"🔄 {description}...")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=os.getcwd())
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} - Failed")
            print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description} - Error: {str(e)}")
        return False

def main():
    print("🔗 GitHub Connection Setup")
    print("=" * 40)

    # Check if remote origin already exists
    result = subprocess.run("git remote -v", shell=True, capture_output=True, text=True)
    if "origin" in result.stdout:
        print("⚠️  Remote 'origin' already exists!")
        print("Current remotes:")
        print(result.stdout)
        print("\nIf you want to change it, first run: git remote remove origin")
        return False

    # Get repository URL from user
    print("📝 Please provide your GitHub repository URL:")
    print("Example: https://github.com/yourusername/naukri-agent.git")
    print("         git@github.com:yourusername/naukri-agent.git")
    print()

    repo_url = input("Repository URL: ").strip()

    if not repo_url:
        print("❌ No URL provided. Exiting.")
        return False

    # Validate URL format
    if not (repo_url.startswith("https://github.com/") or repo_url.startswith("git@github.com:")):
        print("⚠️  URL doesn't look like a GitHub repository URL.")
        print("Expected format: https://github.com/username/repo.git")
        proceed = input("Continue anyway? (y/N): ").lower().strip()
        if proceed != 'y':
            return False

    # Add remote
    if not run_command(f'git remote add origin "{repo_url}"', "Add GitHub remote"):
        return False

    # Push to GitHub
    if not run_command("git push -u origin master", "Push to GitHub"):
        return False

    print()
    print("🎉 Successfully connected to GitHub!")
    print(f"📍 Repository: {repo_url}")
    print("🌐 View your repository at: " + repo_url.replace('.git', '').replace('git@github.com:', 'https://github.com/'))
    print()
    print("📋 Next steps:")
    print("- Your code is now on GitHub!")
    print("- You can clone it on other machines")
    print("- Set up GitHub Actions for CI/CD if needed")
    print("- Share the repository with collaborators")

    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user.")
        sys.exit(1)