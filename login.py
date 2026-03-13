"""
Login module for Naukri Agent
"""

import os
from playwright.sync_api import Page, Browser, BrowserContext
from dotenv import load_dotenv
from utils.logger import setup_logger
from config import NAUKRI_LOGIN_URL, PAGE_LOAD_TIMEOUT, ELEMENT_WAIT_TIMEOUT

# Load environment variables
load_dotenv()

logger = setup_logger(__name__)


class NaukriLogin:
    """Handles login functionality for Naukri"""

    def __init__(self, browser: Browser):
        self.browser = browser
        self.email = os.getenv("NAUKRI_EMAIL")
        self.password = os.getenv("NAUKRI_PASSWORD")

        if not self.email or not self.password:
            raise ValueError("NAUKRI_EMAIL and NAUKRI_PASSWORD must be set in environment variables")

    def login(self) -> BrowserContext:
        """
        Perform login to Naukri

        Returns:
            BrowserContext: Authenticated browser context
        """
        logger.info("Starting Naukri login process")

        # Create a new context for this session
        context = self.browser.new_context()

        try:
            page = context.new_page()
            page.set_default_timeout(PAGE_LOAD_TIMEOUT * 1000)

            logger.info(f"Navigating to login page: {NAUKRI_LOGIN_URL}")
            page.goto(NAUKRI_LOGIN_URL)

            # Wait for page to load
            page.wait_for_load_state("networkidle")

            # Fill email
            logger.info("Filling email field")
            email_selector = 'input[placeholder*="email"]'
            page.wait_for_selector(email_selector, timeout=ELEMENT_WAIT_TIMEOUT * 1000)
            page.fill(email_selector, self.email)

            # Fill password
            logger.info("Filling password field")
            password_selector = 'input[type="password"]'
            page.wait_for_selector(password_selector, timeout=ELEMENT_WAIT_TIMEOUT * 1000)
            page.fill(password_selector, self.password)

            # Click login button
            logger.info("Clicking login button")
            login_button_selector = 'button[type="submit"]'
            page.wait_for_selector(login_button_selector, timeout=ELEMENT_WAIT_TIMEOUT * 1000)
            page.click(login_button_selector)

            # Wait for navigation after login
            page.wait_for_load_state("networkidle")

            # Check if login was successful
            if "login" in page.url.lower() or page.locator('text="Invalid"').is_visible():
                raise Exception("Login failed. Please check credentials.")

            logger.info("Login successful")
            return context

        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            context.close()
            raise