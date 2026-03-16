#!/usr/bin/env python3
"""
Job Application Module
Automatically applies to jobs based on resume keywords and matching criteria
"""

import time
import random
from typing import List, Dict, Optional
from playwright.sync_api import BrowserContext, Page
from utils.logger import setup_logger
from resume_reader import ResumeReader
from job_search import JobSearch
from config import PAGE_LOAD_TIMEOUT, ELEMENT_WAIT_TIMEOUT

logger = setup_logger(__name__)


class JobApplier:
    """Handles automatic job applications based on resume matching"""

    def __init__(self, context: BrowserContext):
        self.context = context
        self.resume_reader = ResumeReader()
        self.job_search = JobSearch(context)

    def get_target_keywords(self) -> List[str]:
        """
        Get the most relevant keywords for job searching and application

        Returns:
            List of target keywords
        """
        keywords = self.resume_reader.generate_job_search_keywords()

        # Prioritize ServiceNow administrator keywords
        priority_keywords = [
            "servicenow administrator",
            "itsm administrator",
            "servicenow developer",
            "servicenow consultant",
            "servicenow system administrator"
        ]

        # Combine priority keywords with generated ones
        all_keywords = priority_keywords + keywords
        unique_keywords = list(set(all_keywords))

        logger.info(f"Using {len(unique_keywords)} target keywords for job application")
        return unique_keywords[:15]  # Limit to top 15

    def search_and_apply_jobs(self, max_applications: int = 5) -> Dict[str, int]:
        """
        Search for jobs using resume keywords and apply to matching positions

        Args:
            max_applications: Maximum number of applications to submit

        Returns:
            Dict with application statistics
        """
        logger.info(f"Starting job search and application process (max: {max_applications})")

        keywords = self.get_target_keywords()
        applied_count = 0
        searched_count = 0
        errors_count = 0

        for keyword in keywords:
            if applied_count >= max_applications:
                logger.info(f"Reached maximum applications limit: {max_applications}")
                break

            try:
                logger.info(f"Searching for jobs with keyword: '{keyword}'")

                # Search for jobs
                jobs = self.job_search.search_jobs(keyword, max_results=10)
                searched_count += len(jobs)

                logger.info(f"Found {len(jobs)} jobs for '{keyword}'")

                # Apply to jobs
                for job in jobs:
                    if applied_count >= max_applications:
                        break

                    try:
                        if self._should_apply_to_job(job):
                            success = self._apply_to_job(job)
                            if success:
                                applied_count += 1
                                logger.info(f"✅ Successfully applied to job: {job.get('title', 'Unknown')}")
                            else:
                                logger.warning(f"❌ Failed to apply to job: {job.get('title', 'Unknown')}")
                        else:
                            logger.info(f"⏭️ Skipped job (not matching criteria): {job.get('title', 'Unknown')}")

                    except Exception as e:
                        logger.error(f"Error applying to job {job.get('title', 'Unknown')}: {str(e)}")
                        errors_count += 1

                    # Add delay between applications to avoid being flagged
                    time.sleep(random.uniform(3, 8))

            except Exception as e:
                logger.error(f"Error searching with keyword '{keyword}': {str(e)}")
                errors_count += 1

            # Add delay between keyword searches
            time.sleep(random.uniform(5, 10))

        stats = {
            'jobs_searched': searched_count,
            'applications_submitted': applied_count,
            'errors': errors_count
        }

        logger.info(f"Job application process completed: {stats}")
        return stats

    def _should_apply_to_job(self, job: Dict) -> bool:
        """
        Determine if we should apply to a specific job based on matching criteria

        Args:
            job: Job information dictionary

        Returns:
            bool: True if we should apply
        """
        title = job.get('title', '').lower()
        company = job.get('company', '').lower()
        description = job.get('description', '').lower()

        # Must-have keywords for ServiceNow Administrator role
        required_keywords = [
            'servicenow', 'administrator', 'itsm', 'itil'
        ]

        # Nice-to-have keywords
        preferred_keywords = [
            'system administrator', 'developer', 'consultant',
            'incident management', 'change management', 'service catalog'
        ]

        # Check if job title contains required keywords
        title_matches = any(keyword in title for keyword in required_keywords)

        # Check if description contains relevant keywords
        desc_matches = any(keyword in description for keyword in required_keywords + preferred_keywords)

        # Experience level check (avoid very senior roles)
        senior_keywords = ['lead', 'principal', 'architect', 'manager', 'director']
        is_senior = any(keyword in title for keyword in senior_keywords)

        # Company filter (avoid mass recruiters, staffing agencies)
        avoid_companies = [
            'recruitment', 'staffing', 'placement', 'consulting services',
            ' Naukri', 'monster', 'indeed'  # Job portals themselves
        ]
        avoid_company = any(avoid in company for avoid in avoid_companies)

        should_apply = (title_matches or desc_matches) and not is_senior and not avoid_company

        logger.debug(f"Job '{title}' - Apply: {should_apply} (title_match: {title_matches}, desc_match: {desc_matches}, senior: {is_senior}, avoid_company: {avoid_company})")

        return should_apply

    def _apply_to_job(self, job: Dict) -> bool:
        """
        Apply to a specific job

        Args:
            job: Job information dictionary

        Returns:
            bool: True if application was successful
        """
        try:
            page = self.context.new_page()
            page.set_default_timeout(PAGE_LOAD_TIMEOUT * 1000)

            job_url = job.get('url', '')
            if not job_url:
                logger.warning("No URL provided for job application")
                return False

            logger.info(f"Applying to job: {job.get('title', 'Unknown')}")

            # Navigate to job page
            page.goto(job_url)
            page.wait_for_load_state("networkidle")

            # Look for apply button/link
            apply_selectors = [
                'button:has-text("Apply")',
                'a:has-text("Apply")',
                'button:has-text("Apply Now")',
                'a:has-text("Apply Now")',
                '[data-testid*="apply"]',
                '.apply-btn',
                '.apply-button'
            ]

            apply_button = None
            for selector in apply_selectors:
                try:
                    page.wait_for_selector(selector, timeout=5000)
                    apply_button = page.locator(selector).first
                    if apply_button.is_visible():
                        logger.info(f"Found apply button with selector: {selector}")
                        break
                except:
                    continue

            if not apply_button:
                logger.warning("Apply button not found on job page")
                page.close()
                return False

            # Click apply button
            apply_button.click()
            page.wait_for_load_state("networkidle")

            # Check if application was successful
            success_indicators = [
                'text="Application submitted"',
                'text="Applied successfully"',
                'text="Your application has been sent"',
                'text="Application received"',
                '.success-message',
                '[data-testid*="success"]'
            ]

            application_successful = False
            for indicator in success_indicators:
                try:
                    page.wait_for_selector(indicator, timeout=5000)
                    application_successful = True
                    logger.info("Application submitted successfully")
                    break
                except:
                    continue

            # If no explicit success message, check if we're on a different page
            if not application_successful:
                current_url = page.url
                if 'apply' in current_url.lower() or 'application' in current_url.lower():
                    logger.info("Application process initiated (on application page)")
                    application_successful = True

            page.close()
            return application_successful

        except Exception as e:
            logger.error(f"Error during job application: {str(e)}")
            try:
                page.close()
            except:
                pass
            return False


if __name__ == "__main__":
    # Test the job applier (requires browser context)
    print("JobApplier module loaded successfully")
    print("Use this module through the main scheduler for job applications")