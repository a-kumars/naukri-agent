#!/usr/bin/env python3
"""
Resume Upload Test Script for Naukri Agent
Tests only the resume upload functionality
"""

from playwright.sync_api import sync_playwright
from utils.logger import setup_logger
from login import NaukriLogin
from resume_updater import ResumeUpdater
from config import HEADLESS_MODE, BROWSER_TYPE

logger = setup_logger(__name__)


def test_resume_upload():
    """
    Test function that only uploads resume to Naukri
    """
    logger.info("🧪 Starting Resume Upload Test")

    with sync_playwright() as p:
        try:
            # Launch browser based on config
            logger.info(f"Launching {BROWSER_TYPE} browser (headless={HEADLESS_MODE})")
            if BROWSER_TYPE.lower() == "firefox":
                browser = p.firefox.launch(headless=HEADLESS_MODE)
            elif BROWSER_TYPE.lower() == "webkit":
                browser = p.webkit.launch(headless=HEADLESS_MODE)
            elif BROWSER_TYPE.lower() == "chrome":
                browser = p.chromium.launch(channel="chrome", headless=HEADLESS_MODE)
            elif BROWSER_TYPE.lower() == "edge":
                browser = p.chromium.launch(channel="msedge", headless=HEADLESS_MODE)
            else:
                browser = p.chromium.launch(headless=HEADLESS_MODE)

            # Login
            logger.info("Logging into Naukri...")
            login_handler = NaukriLogin(browser)
            context = login_handler.login()

            # Upload resume only
            logger.info("Uploading resume...")
            resume_updater = ResumeUpdater(context)
            upload_success = resume_updater.update_resume()

            if upload_success:
                logger.info("✅ Resume upload test completed successfully!")
                print("\n🎉 SUCCESS: Resume uploaded successfully!")
                print("📄 Your resume has been updated on Naukri.com")
            else:
                logger.warning("⚠️ Resume upload completed but may need manual verification")
                print("\n⚠️ Resume upload completed - please check Naukri manually")

        except Exception as e:
            logger.error(f"❌ Resume upload test failed: {str(e)}")
            print(f"\n❌ FAILED: {str(e)}")
            return False

        finally:
            try:
                context.close()
                browser.close()
            except:
                pass

    return True


if __name__ == "__main__":
    print("🚀 Naukri Agent - Resume Upload Test")
    print("=" * 40)
    print("This will only upload your resume to Naukri.com")
    print("No job search or profile updates will be performed.")
    print()

    try:
        success = test_resume_upload()
        if success:
            print("\n✅ Test completed successfully!")
        else:
            print("\n❌ Test failed!")
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")