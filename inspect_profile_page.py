"""
Inspect Naukri profile page to find resume upload elements
"""

import os
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
from utils.logger import setup_logger
from config import NAUKRI_LOGIN_URL, PAGE_LOAD_TIMEOUT

# Load environment variables
load_dotenv()

logger = setup_logger(__name__)

def inspect_profile_page():
    """Inspect the Naukri profile page to find resume upload elements"""

    email = os.getenv("NAUKRI_EMAIL")
    password = os.getenv("NAUKRI_PASSWORD")

    if not email or not password:
        raise ValueError("NAUKRI_EMAIL and NAUKRI_PASSWORD must be set")

    logger.info("Starting profile page inspection")

    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(channel="chrome", headless=False)

        try:
            context = browser.new_context()
            page = context.new_page()
            page.set_default_timeout(PAGE_LOAD_TIMEOUT * 1000)

            logger.info(f"Navigating to login page: {NAUKRI_LOGIN_URL}")
            page.goto(NAUKRI_LOGIN_URL)
            page.wait_for_load_state("networkidle")

            # Login
            logger.info("Logging in...")
            email_input = page.locator('input[placeholder*="Email"]').first
            if email_input.is_visible():
                email_input.fill(email)

            password_input = page.locator('input[type="password"]').first
            if password_input.is_visible():
                password_input.fill(password)

            login_button = page.locator('button[type="submit"]').first
            if login_button.is_visible():
                login_button.click()

            # Wait for navigation
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(3000)

            logger.info(f"After login, URL: {page.url}")

            # Navigate to profile page
            logger.info("Navigating to profile page...")
            try:
                page.goto("https://www.naukri.com/mnjuser/profile", timeout=30000)
                page.wait_for_load_state("networkidle", timeout=30000)
                page.wait_for_timeout(5000)  # Extra wait for dynamic content
            except Exception as e:
                logger.warning(f"Profile page load timed out: {e}")
                # Try to continue anyway
                page.wait_for_timeout(2000)

            logger.info(f"Profile page URL: {page.url}")
            logger.info(f"Profile page title: {page.title()}")

            # Take screenshot
            page.screenshot(path="debug_profile_page.png")
            logger.info("Profile page screenshot saved")

            # Look for resume-related navigation or sections
            resume_nav_selectors = [
                'a:has-text("Resume")',
                'a:has-text("CV")',
                'button:has-text("Resume")',
                'button:has-text("CV")',
                '[data-testid*="resume"]',
                '[class*="resume"]',
                'text="Resume"',
                'text="CV"'
            ]

            logger.info("Looking for resume navigation elements...")
            for selector in resume_nav_selectors:
                try:
                    elements = page.query_selector_all(selector)
                    if elements:
                        logger.info(f"Found {len(elements)} elements with selector: {selector}")
                        for i, elem in enumerate(elements[:3]):  # First 3
                            text = elem.text_content().strip()
                            href = elem.get_attribute('href') or ''
                            logger.info(f"  Element {i}: text='{text}', href='{href}'")
                except:
                    pass

            # Look for "Update" button/link under resume section
            update_selectors = [
                'a:has-text("Update")',
                'button:has-text("Update")',
                '[class*="update"]',
                '[data-testid*="update"]',
                'text="Update"'
            ]

            logger.info("Looking for Update button/link...")
            update_found = False
            for selector in update_selectors:
                try:
                    elements = page.query_selector_all(selector)
                    if elements:
                        logger.info(f"Found {len(elements)} Update elements with selector: {selector}")
                        for i, elem in enumerate(elements):
                            try:
                                text = elem.text_content().strip()
                                tag = elem.evaluate("el => el.tagName.toLowerCase()")
                                logger.info(f"  Update Element {i}: tag='{tag}', text='{text}'")

                            # Check if this Update is under resume section
                            try:
                                # Look for resume-related parent elements
                                parent = elem.query_selector('xpath=ancestor::*[contains(text(), "Resume") or contains(@class, "resume") or contains(@id, "resume")]')
                                if parent:
                                    logger.info(f"    This Update appears to be under resume section!")
                                    update_found = True

                                    # Click the Update button
                                    logger.info("    Clicking Update button...")
                                    elem.click()
                                    page.wait_for_load_state('networkidle', timeout=10000)
                                    logger.info(f"    After Update click - URL: {page.url}")
                                    logger.info(f"    After Update click - Title: {page.title()}")

                                    # Take screenshot of the update page
                                    page.screenshot(path="debug_resume_update_page.png")
                                    logger.info("    Resume update page screenshot saved")

                                    # Look for file upload elements on the update page
                                    file_input_selectors = [
                                        'input[type="file"]',
                                        '[class*="upload"] input[type="file"]',
                                        '[class*="file"] input[type="file"]',
                                        'input[accept*="pdf"]',
                                        'input[accept*="doc"]',
                                        'input[accept*="docx"]'
                                    ]

                                    logger.info("    Looking for file upload inputs...")
                                    for file_selector in file_input_selectors:
                                        try:
                                            file_inputs = page.query_selector_all(file_selector)
                                            if file_inputs:
                                                logger.info(f"      Found {len(file_inputs)} file inputs with selector: {file_selector}")
                                                for j, file_input in enumerate(file_inputs):
                                                    accept = file_input.get_attribute('accept') or ''
                                                    name = file_input.get_attribute('name') or ''
                                                    id_attr = file_input.get_attribute('id') or ''
                                                    logger.info(f"        File input {j}: accept='{accept}', name='{name}', id='{id_attr}'")
                                        except Exception as e:
                                            logger.error(f"      Error checking file selector {file_selector}: {e}")

                                    # Look for upload/submit buttons
                                    upload_buttons = [
                                        'button:has-text("Upload")',
                                        'button:has-text("Submit")',
                                        'button:has-text("Save")',
                                        'input[type="submit"]',
                                        '[class*="upload"] button',
                                        '[class*="submit"] button'
                                    ]

                                    logger.info("    Looking for upload/submit buttons...")
                                    for btn_selector in upload_buttons:
                                        try:
                                            buttons = page.query_selector_all(btn_selector)
                                            if buttons:
                                                logger.info(f"      Found {len(buttons)} buttons with selector: {btn_selector}")
                                                for j, btn in enumerate(buttons):
                                                    btn_text = btn.text_content().strip()
                                                    logger.info(f"        Button {j}: text='{btn_text}'")
                                        except Exception as e:
                                            logger.error(f"      Error checking button selector {btn_selector}: {e}")

                                    break  # Found the resume update page, stop looking
                            except Exception as e:
                                logger.error(f"    Error checking parent for Update element {i}: {e}")

                        if update_found:
                            break  # Found and processed the Update button
                except Exception as e:
                    logger.error(f"Error checking Update selector {selector}: {e}")

            if not update_found:
                logger.warning("No Update button found under resume section")

            # Inspect all input elements
            all_inputs = page.query_selector_all('input')
            logger.info(f"Found {len(all_inputs)} input elements on profile page:")
            for i, inp in enumerate(all_inputs):
                input_type = inp.get_attribute('type') or 'text'
                placeholder = inp.get_attribute('placeholder') or ''
                name = inp.get_attribute('name') or ''
                id_attr = inp.get_attribute('id') or ''
                class_attr = inp.get_attribute('class') or ''
                logger.info(f"  Input {i}: type={input_type}, placeholder='{placeholder}', name='{name}', id='{id_attr}', class='{class_attr}'")

            # Look for file inputs specifically
            file_inputs = page.query_selector_all('input[type="file"]')
            logger.info(f"Found {len(file_inputs)} file input elements:")
            for i, inp in enumerate(file_inputs):
                id_attr = inp.get_attribute('id') or ''
                name = inp.get_attribute('name') or ''
                class_attr = inp.get_attribute('class') or ''
                accept = inp.get_attribute('accept') or ''
                logger.info(f"  File Input {i}: id='{id_attr}', name='{name}', class='{class_attr}', accept='{accept}'")

            # Look for buttons that might be upload buttons
            buttons = page.query_selector_all('button')
            logger.info(f"Found {len(buttons)} button elements:")
            for i, btn in enumerate(buttons[:20]):  # Limit to first 20
                text = btn.text_content().strip()
                id_attr = btn.get_attribute('id') or ''
                class_attr = btn.get_attribute('class') or ''
                if text or id_attr or class_attr:
                    logger.info(f"  Button {i}: text='{text}', id='{id_attr}', class='{class_attr}'")

            # Look for elements containing "resume" or "upload"
            resume_elements = page.query_selector_all('[class*="resume"], [class*="upload"], [id*="resume"], [id*="upload"]')
            logger.info(f"Found {len(resume_elements)} elements with resume/upload in class/id:")
            for i, elem in enumerate(resume_elements[:10]):  # Limit to first 10
                tag = elem.evaluate("el => el.tagName")
                id_attr = elem.get_attribute('id') or ''
                class_attr = elem.get_attribute('class') or ''
                text = elem.text_content().strip()[:100]  # First 100 chars
                logger.info(f"  Element {i}: tag={tag}, id='{id_attr}', class='{class_attr}', text='{text}'")

            # Save page HTML for analysis
            html_content = page.content()
            with open('debug_profile_page.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info("Profile page HTML saved to debug_profile_page.html")

        finally:
            context.close()
            browser.close()

if __name__ == "__main__":
    inspect_profile_page()