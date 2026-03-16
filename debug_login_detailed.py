"""
Debug script to capture detailed login page information
"""

import os
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
from utils.logger import setup_logger
from config import NAUKRI_LOGIN_URL, PAGE_LOAD_TIMEOUT

# Load environment variables
load_dotenv()

logger = setup_logger(__name__)

def debug_login():
    """Debug login process with detailed page analysis"""

    email = os.getenv("NAUKRI_EMAIL")
    password = os.getenv("NAUKRI_PASSWORD")

    if not email or not password:
        raise ValueError("NAUKRI_EMAIL and NAUKRI_PASSWORD must be set")

    logger.info("Starting detailed login debug")

    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False)

        try:
            context = browser.new_context()
            page = context.new_page()
            page.set_default_timeout(PAGE_LOAD_TIMEOUT * 1000)

            logger.info(f"Navigating to: {NAUKRI_LOGIN_URL}")
            page.goto(NAUKRI_LOGIN_URL)
            page.wait_for_load_state("networkidle")

            # Take initial screenshot
            page.screenshot(path="debug_initial_page.png")
            logger.info("Initial page screenshot saved")

            # Log all inputs on the page
            all_inputs = page.query_selector_all('input')
            logger.info(f"Found {len(all_inputs)} input elements:")
            for i, inp in enumerate(all_inputs):
                input_type = inp.get_attribute('type') or 'text'
                placeholder = inp.get_attribute('placeholder') or ''
                name = inp.get_attribute('name') or ''
                id_attr = inp.get_attribute('id') or ''
                logger.info(f"  Input {i}: type={input_type}, placeholder='{placeholder}', name='{name}', id='{id_attr}'")

            # Find and fill email
            email_input = page.locator('input[placeholder*="Email"]').first
            if email_input.is_visible():
                logger.info("Filling email field")
                email_input.fill(email)
                page.wait_for_timeout(1000)  # Wait a bit

            # Find and fill password
            password_input = page.locator('input[type="password"]').first
            if password_input.is_visible():
                logger.info("Filling password field")
                password_input.fill(password)
                page.wait_for_timeout(1000)  # Wait a bit

            # Take screenshot before clicking login
            page.screenshot(path="debug_before_login_click.png")
            logger.info("Screenshot before login click saved")

            # Click login
            login_button = page.locator('button[type="submit"]').first
            if login_button.is_visible():
                logger.info("Clicking login button")
                login_button.click()

                # Wait longer for any dynamic content
                page.wait_for_timeout(5000)

                # Take screenshot after login attempt
                page.screenshot(path="debug_after_login_click.png")
                logger.info("Screenshot after login click saved")

                # Log current URL
                logger.info(f"Current URL after login: {page.url}")

                # Log page title
                logger.info(f"Page title: {page.title()}")

                # Capture all visible text on the page
                try:
                    all_text = page.evaluate("""
                        () => {
                            const elements = document.querySelectorAll('*');
                            let text = '';
                            for (let elem of elements) {
                                const style = window.getComputedStyle(elem);
                                if (style.display !== 'none' && style.visibility !== 'hidden' && elem.textContent) {
                                    const trimmed = elem.textContent.trim();
                                    if (trimmed && trimmed.length > 2) {  // Ignore very short text
                                        text += trimmed + '\\n';
                                    }
                                }
                            }
                            return text;
                        }
                    """)

                    # Save text to file
                    with open('debug_page_text.txt', 'w', encoding='utf-8') as f:
                        f.write(all_text)
                    logger.info("Page text saved to debug_page_text.txt")

                    # Look for common error patterns
                    error_patterns = ['invalid', 'incorrect', 'wrong', 'failed', 'error', 'please check', 'captcha', 'verification']
                    found_errors = []
                    for pattern in error_patterns:
                        if pattern.lower() in all_text.lower():
                            found_errors.append(pattern)

                    if found_errors:
                        logger.warning(f"Found potential error patterns: {found_errors}")
                    else:
                        logger.info("No obvious error patterns found in page text")

                except Exception as e:
                    logger.error(f"Error capturing page text: {e}")

                # Check for CAPTCHA or verification elements
                captcha_selectors = [
                    '[class*="captcha"]',
                    '[id*="captcha"]',
                    'iframe[src*="captcha"]',
                    'iframe[src*="recaptcha"]',
                    '[class*="recaptcha"]',
                    'text="CAPTCHA"',
                    'text="captcha"',
                    'text="verification"',
                    'text="verify"'
                ]

                captcha_found = False
                for selector in captcha_selectors:
                    try:
                        if page.locator(selector).count() > 0:
                            logger.warning(f"Found potential CAPTCHA element: {selector}")
                            captcha_found = True
                    except:
                        continue

                if captcha_found:
                    logger.warning("CAPTCHA or verification elements detected on the page")
                else:
                    logger.info("No CAPTCHA elements detected")

            else:
                logger.error("Login button not found")

        finally:
            context.close()
            browser.close()

if __name__ == "__main__":
    debug_login()