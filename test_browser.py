#!/usr/bin/env python3
"""
Browser Test Script for Naukri Agent
Test different browsers before running the full agent
"""

from playwright.sync_api import sync_playwright
from config import BROWSER_TYPE, HEADLESS_MODE
from utils.logger import setup_logger

logger = setup_logger(__name__)


def test_browser():
    """Test the selected browser"""
    print(f"🧪 Testing {BROWSER_TYPE} browser (headless={HEADLESS_MODE})")
    print("=" * 50)

    try:
        with sync_playwright() as p:
            # Launch browser based on config
            if BROWSER_TYPE.lower() == "firefox":
                browser = p.firefox.launch(headless=HEADLESS_MODE)
                browser_name = "Firefox"
            elif BROWSER_TYPE.lower() == "webkit":
                browser = p.webkit.launch(headless=HEADLESS_MODE)
                browser_name = "WebKit (Safari)"
            else:
                browser = p.chromium.launch(headless=HEADLESS_MODE)
                browser_name = "Chromium"

            print(f"✅ {browser_name} browser launched successfully")

            # Test basic navigation
            page = browser.new_page()
            page.goto("https://www.google.com")
            title = page.title()
            print(f"✅ Page navigation works - Title: {title}")

            # Close browser
            browser.close()

            print(f"✅ {browser_name} browser test completed successfully!")
            print(f"🎯 Ready to use {browser_name} for Naukri Agent")

            return True

    except Exception as e:
        print(f"❌ Browser test failed: {str(e)}")
        print("💡 Try changing BROWSER_TYPE in config.py to:")
        print("   - 'chromium' (default)")
        print("   - 'firefox'")
        print("   - 'webkit'")
        return False


def show_browser_options():
    """Show available browser options"""
    print("🌐 Available Browser Options:")
    print("• chromium - Google Chrome/Chromium (default, most compatible)")
    print("• firefox - Mozilla Firefox (good alternative)")
    print("• webkit - WebKit/Safari (limited compatibility)")
    print()
    print("To change browser, edit BROWSER_TYPE in config.py")


if __name__ == "__main__":
    show_browser_options()
    print()
    success = test_browser()
    if success:
        print()
        print("🚀 Run 'python main.py' to start the Naukri Agent with this browser")
    else:
        print()
        print("🔧 Fix browser issues before running the full agent")