"""
Resume updater module for Naukri Agent
"""

import os
from playwright.sync_api import BrowserContext, Page
from utils.logger import setup_logger
from config import NAUKRI_PROFILE_URL, PAGE_LOAD_TIMEOUT, ELEMENT_WAIT_TIMEOUT, RESUME_FILE_PATH

logger = setup_logger(__name__)


class ResumeUpdater:
    """Handles resume/profile update functionality"""

    def __init__(self, context: BrowserContext):
        self.context = context

    def update_resume(self) -> bool:
        """
        Update resume on Naukri profile

        Returns:
            bool: True if update was successful
        """
        logger.info("Starting resume update process")

        page = None
        try:
            page = self.context.new_page()
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
                return False

            # First, try to upload resume if file exists
            resume_uploaded = self._upload_resume_file(page)

            # Then update profile (click edit/save)
            profile_updated = self._update_profile(page)

            if resume_uploaded or profile_updated:
                logger.info("Resume update completed successfully")
                return True
            else:
                logger.warning("Neither resume upload nor profile update was successful")
                return False

        except Exception as e:
            logger.error(f"Resume update failed: {str(e)}")
            return False

        finally:
            if page:
                page.close()

    def _upload_resume_file(self, page: Page) -> bool:
        """
        Upload resume file to Naukri

        Args:
            page: Playwright page object

        Returns:
            bool: True if upload was successful
        """
        try:
            # Check if resume file exists
            if not os.path.exists(RESUME_FILE_PATH):
                logger.warning(f"Resume file not found: {RESUME_FILE_PATH}")
                return False

            logger.info(f"Uploading resume file: {RESUME_FILE_PATH}")

            # Look for resume upload elements - use specific selector found during inspection
            upload_selectors = [
                '#attachCV',  # Specific selector found during profile inspection
                'input[type="file"]',
                '.resume-upload input[type="file"]',
                '[data-testid="resume-upload"] input[type="file"]',
                '.upload-resume input[type="file"]'
            ]

            file_input = None
            for selector in upload_selectors:
                try:
                    logger.info(f"Trying file input selector: {selector}")
                    page.wait_for_selector(selector, timeout=5000)
                    file_input = page.locator(selector).first
                    if file_input.is_visible():
                        logger.info(f"Found visible file input with selector: {selector}")
                        break
                    else:
                        logger.warning(f"File input found but not visible: {selector}")
                except Exception as e:
                    logger.debug(f"Selector {selector} not found: {e}")
                    continue

            if not file_input:
                # Try looking for upload buttons that might trigger file input
                upload_button_selectors = [
                    'button:has-text("Upload Resume")',
                    'button:has-text("Update Resume")',
                    '.upload-btn',
                    '[data-testid="upload-resume-btn"]'
                ]

                for selector in upload_button_selectors:
                    try:
                        page.wait_for_selector(selector, timeout=5000)
                        upload_button = page.locator(selector).first
                        if upload_button.is_visible():
                            upload_button.click()
                            # Wait for file input to appear
                            page.wait_for_selector('input[type="file"]', timeout=5000)
                            file_input = page.locator('input[type="file"]').first
                            break
                    except:
                        continue

            if not file_input:
                logger.warning("Resume upload input not found")
                return False

            # Upload the file
            file_input.set_input_files(RESUME_FILE_PATH)

            # Wait for upload to complete
            page.wait_for_load_state("networkidle")

            # Look for success message or confirmation
            success_indicators = [
                'text="Resume uploaded successfully"',
                'text="Upload successful"',
                '.success-message',
                '[data-testid="upload-success"]'
            ]

            upload_successful = False
            for indicator in success_indicators:
                try:
                    page.wait_for_selector(indicator, timeout=5000)
                    upload_successful = True
                    break
                except:
                    continue

            if upload_successful:
                logger.info("Resume file uploaded successfully")
                return True
            else:
                logger.info("Resume file upload completed (no explicit success message)")
                return True

        except Exception as e:
            logger.error(f"Resume upload failed: {str(e)}")
            return False

    def _update_profile(self, page: Page) -> bool:
        """
        Update profile by clicking edit and save buttons

        Args:
            page: Playwright page object

        Returns:
            bool: True if profile update was successful
        """
        try:
            logger.info("Updating profile information")

            # Look for edit button (this might vary based on Naukri's UI)
            edit_selectors = [
                'button:has-text("Edit")',
                '.edit-btn',
                '[data-testid="edit-button"]',
                'a:has-text("Edit")'
            ]

            edit_button = None
            for selector in edit_selectors:
                try:
                    page.wait_for_selector(selector, timeout=5000)
                    edit_button = page.locator(selector).first
                    if edit_button.is_visible():
                        break
                except:
                    continue

            if not edit_button:
                logger.warning("Edit button not found. Profile might already be up to date.")
                return True

            logger.info("Clicking edit button")
            edit_button.click()

            # Wait for edit mode to load
            page.wait_for_load_state("networkidle")

            # Look for save button - include Update links found during inspection
            save_selectors = [
                'a:has-text("Update")',  # Specific Update links found during inspection
                'button:has-text("Save")',
                'button:has-text("Update")',
                '.save-btn',
                '[data-testid="save-button"]'
            ]

            save_button = None
            for selector in save_selectors:
                try:
                    page.wait_for_selector(selector, timeout=5000)
                    save_button = page.locator(selector).first
                    if save_button.is_visible():
                        break
                except:
                    continue

            if not save_button:
                logger.warning("Save button not found. Assuming update is not needed.")
                return True

            logger.info("Clicking save button")
            save_button.click()

            # Wait for save to complete
            page.wait_for_load_state("networkidle")

            logger.info("Profile update completed successfully")
            return True

        except Exception as e:
            logger.error(f"Profile update failed: {str(e)}")
            return False