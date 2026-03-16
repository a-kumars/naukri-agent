"""
Scheduler module for Naukri Agent
"""

from playwright.sync_api import sync_playwright
from utils.logger import setup_logger
from login import NaukriLogin
from resume_updater import ResumeUpdater
from job_search import JobSearch
from storage import JobStorage
from job_applier import JobApplier
from config import HEADLESS_MODE, BROWSER_TYPE, PAGE_LOAD_TIMEOUT, NAUKRI_PROFILE_URL

logger = setup_logger(__name__)


def run_resume_only_agent() -> bool:
    """
    Run only resume update (for scheduled tasks)
    Browser closes immediately after resume upload

    Returns:
        bool: True if successful, False otherwise
    """
    logger.info("Starting scheduled resume-only agent execution")

    with sync_playwright() as p:
        try:
            # Launch browser
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
            login_handler = NaukriLogin(browser)
            context = login_handler.login()

            try:
                # Only upload resume (skip profile update for scheduled tasks)
                logger.info("Updating resume (scheduled task)")
                resume_updater = ResumeUpdater(context)

                # Navigate to profile page and upload resume only
                page = context.new_page()
                page.set_default_timeout(PAGE_LOAD_TIMEOUT * 1000)

                logger.info(f"Navigating to profile page: {NAUKRI_PROFILE_URL}")
                page.goto(NAUKRI_PROFILE_URL)

                # Wait for page to load completely
                page.wait_for_load_state("networkidle")
                logger.info("Profile page loaded, waiting for resume section...")

                # Wait for resume section to be visible (may need scrolling)
                resume_section_selectors = [
                    '#resume360',  # Found in inspection
                    '.resume-name-inline',
                    '[class*="resume"]',
                    'text="Resume"'
                ]

                resume_section_found = False
                for selector in resume_section_selectors:
                    try:
                        page.wait_for_selector(selector, timeout=10000)
                        logger.info(f"Resume section found with selector: {selector}")
                        resume_section_found = True

                        # Scroll to the resume section
                        element = page.locator(selector).first
                        element.scroll_into_view_if_needed()
                        page.wait_for_timeout(2000)  # Wait for scroll to complete
                        break
                    except:
                        continue

                if not resume_section_found:
                    logger.warning("Resume section not found on profile page")
                    page.close()
                    return False

                # Upload resume file only
                resume_success = resume_updater._upload_resume_file(page)

                if resume_success:
                    logger.info("Resume upload completed successfully")
                    page.close()
                    return True
                else:
                    logger.error("Resume upload failed")
                    page.close()
                    return False

            finally:
                # Clean up immediately after resume upload
                logger.info("Closing browser after resume upload")
                context.close()
                browser.close()

        except Exception as e:
            logger.error(f"Resume-only agent execution failed: {str(e)}")
            return False


def run_agent() -> bool:
    """
    Main function to run the Naukri agent

    This function performs:
    1. Login to Naukri
    2. Update resume
    3. Search for jobs
    4. Save jobs to CSV

    Returns:
        bool: True if successful, False otherwise
    """
    logger.info("Starting Naukri Agent execution")

    with sync_playwright() as p:
        try:
            # Launch browser
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
            login_handler = NaukriLogin(browser)
            context = login_handler.login()

            success = True

            try:
                # Update resume
                logger.info("Updating resume")
                resume_updater = ResumeUpdater(context)
                resume_success = resume_updater.update_resume()
                if not resume_success:
                    logger.warning("Resume update failed, but continuing with job search")
                    success = False

                # Search jobs
                logger.info("Searching for jobs")
                job_search = JobSearch(context)
                jobs = job_search.search_jobs()

                # Save jobs
                logger.info("Saving jobs to storage")
                storage = JobStorage()
                saved_count = storage.save_jobs(jobs)

                logger.info(f"Agent execution completed. Saved {saved_count} new jobs.")

            finally:
                # Clean up
                context.close()
                browser.close()

            return success

        except Exception as e:
            logger.error(f"Agent execution failed: {str(e)}")
            return False


if __name__ == "__main__":
    # For testing purposes
    run_agent()