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

            # Fill email - try multiple selectors
            logger.info("Filling email field")
            email_selectors = [
                '#usernameField',
                'input[placeholder*="email"]',
                'input[placeholder*="Email"]',
                'input[type="email"]',
                'input[name*="email"]',
                'input[id*="email"]',
                '#emailTxt',
                '.email input',
                '[data-testid="email-input"]'
            ]

            email_input = None
            for selector in email_selectors:
                try:
                    page.wait_for_selector(selector, timeout=2000)
                    email_input = page.locator(selector).first
                    if email_input.is_visible():
                        logger.info(f"Found email input with selector: {selector}")
                        break
                except:
                    continue

            if not email_input:
                logger.warning("Email input not found with standard selectors, trying to inspect page...")
                # Take screenshot for debugging
                page.screenshot(path="debug_login_page.png")
                logger.info("Screenshot saved as debug_login_page.png")

                # Try to find any input that might be email
                all_inputs = page.query_selector_all('input')
                logger.info(f"Found {len(all_inputs)} input elements on page")

                for i, inp in enumerate(all_inputs):
                    input_type = inp.get_attribute('type') or 'text'
                    placeholder = inp.get_attribute('placeholder') or ''
                    name = inp.get_attribute('name') or ''
                    logger.info(f"Input {i}: type={input_type}, placeholder='{placeholder}', name='{name}'")

                raise Exception("Could not find email input field. Page structure may have changed.")

            email_input.fill(self.email)

            # Fill password - try multiple selectors
            logger.info("Filling password field")
            password_selectors = [
                'input[type="password"]',
                'input[placeholder*="password"]',
                'input[placeholder*="Password"]',
                'input[name*="password"]',
                'input[name*="pass"]',
                '#pwd1',
                '.password input',
                '[data-testid="password-input"]'
            ]

            password_input = None
            for selector in password_selectors:
                try:
                    page.wait_for_selector(selector, timeout=2000)
                    password_input = page.locator(selector).first
                    if password_input.is_visible():
                        logger.info(f"Found password input with selector: {selector}")
                        break
                except:
                    continue

            if not password_input:
                raise Exception("Could not find password input field. Page structure may have changed.")

            password_input.fill(self.password)

            # Click login button - try multiple selectors
            logger.info("Clicking login button")
            login_selectors = [
                'button[type="submit"]',
                'button:has-text("Login")',
                'button:has-text("Sign in")',
                'input[type="submit"]',
                '.loginBtn',
                '#loginBtn',
                '[data-testid="login-button"]'
            ]

            login_button = None
            for selector in login_selectors:
                try:
                    page.wait_for_selector(selector, timeout=2000)
                    login_button = page.locator(selector).first
                    if login_button.is_visible():
                        logger.info(f"Found login button with selector: {selector}")
                        break
                except:
                    continue

            if not login_button:
                raise Exception("Could not find login button. Page structure may have changed.")

            login_button.click()

            # Wait for navigation after login
            page.wait_for_load_state("networkidle", timeout=10000)
            logger.info(f"After login, current URL: {page.url}")

            # Additional wait for dynamic content
            page.wait_for_timeout(3000)

            # Check for login failure indicators
            failure_indicators = [
                'text="Invalid"',
                'text="incorrect"',
                'text="wrong"',
                'text="failed"',
                'text="error"',
                'text="Please check"',
                '.error-message',
                '.login-error',
                '[data-testid*="error"]',
                '.err'
            ]

            login_failed = False
            for indicator in failure_indicators:
                try:
                    if page.locator(indicator).is_visible():
                        login_failed = True
                        logger.warning(f"Found login error indicator: {indicator}")
                        break
                except:
                    continue

            # Check if still on login page
            if "login" in page.url.lower() or "signin" in page.url.lower():
                login_failed = True
                logger.warning("Still on login page after attempted login")

            # Check for successful login indicators
            success_indicators = [
                'text="Dashboard"',
                'text="Profile"',
                'text="My Naukri"',
                'text="Home"',
                '.user-menu',
                '.profile-link',
                '[data-testid*="profile"]',
                'text="Mynaukri"'
            ]

            login_successful = False
            for indicator in success_indicators:
                try:
                    if page.locator(indicator).is_visible():
                        login_successful = True
                        logger.info(f"Found login success indicator: {indicator}")
                        break
                except:
                    continue

            if login_failed:
                raise Exception("Login failed. Please check credentials or account status.")
            elif login_successful:
                logger.info("Login successful - found success indicators")
            else:
                logger.info("Login completed - no clear success/failure indicators found, proceeding...")

            return context

        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            context.close()
            raise
