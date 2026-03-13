"""
Scheduler module for Naukri Agent
"""

from playwright.sync_api import sync_playwright
from utils.logger import setup_logger
from login import NaukriLogin
from resume_updater import ResumeUpdater
from job_search import JobSearch
from storage import JobStorage
from config import HEADLESS_MODE, BROWSER_TYPE

logger = setup_logger(__name__)


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