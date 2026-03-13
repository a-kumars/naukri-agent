"""
Job search module for Naukri Agent
"""

from typing import List, Dict
from playwright.sync_api import BrowserContext, Page
from utils.logger import setup_logger
from config import JOB_KEYWORDS, NAUKRI_BASE_URL, PAGE_LOAD_TIMEOUT, ELEMENT_WAIT_TIMEOUT

logger = setup_logger(__name__)


class JobSearch:
    """Handles job search functionality"""

    def __init__(self, context: BrowserContext):
        self.context = context

    def search_jobs(self, keywords: List[str] = None) -> List[Dict]:
        """
        Search for jobs using keywords

        Args:
            keywords: List of keywords to search for. If None, uses config keywords.

        Returns:
            List of job dictionaries
        """
        if keywords is None:
            keywords = JOB_KEYWORDS

        all_jobs = []

        for keyword in keywords:
            logger.info(f"Searching for jobs with keyword: {keyword}")
            jobs = self._search_single_keyword(keyword)
            all_jobs.extend(jobs)

        logger.info(f"Found {len(all_jobs)} jobs in total")
        return all_jobs

    def _search_single_keyword(self, keyword: str) -> List[Dict]:
        """
        Search for jobs using a single keyword

        Args:
            keyword: Search keyword

        Returns:
            List of job dictionaries
        """
        page = None
        jobs = []

        try:
            page = self.context.new_page()
            page.set_default_timeout(PAGE_LOAD_TIMEOUT * 1000)

            # Construct search URL
            search_url = f"{NAUKRI_BASE_URL}/jobapi/v3/search?noOfResults=20&urlType=search_by_key_loc&searchType=adv&keyword={keyword.replace(' ', '%20')}&location="
            logger.info(f"Navigating to search URL: {search_url}")
            page.goto(search_url)

            # Wait for page to load
            page.wait_for_load_state("networkidle")

            # Wait for job results to load
            page.wait_for_selector('.jobTuple', timeout=ELEMENT_WAIT_TIMEOUT * 1000)

            # Extract job information
            job_elements = page.query_selector_all('.jobTuple')

            for job_element in job_elements:
                try:
                    job_data = self._extract_job_data(job_element)
                    if job_data:
                        jobs.append(job_data)
                except Exception as e:
                    logger.warning(f"Failed to extract job data: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"Job search failed for keyword '{keyword}': {str(e)}")

        finally:
            if page:
                page.close()

        return jobs

    def _extract_job_data(self, job_element) -> Dict:
        """
        Extract job data from a job element

        Args:
            job_element: Playwright element handle

        Returns:
            Dictionary with job information
        """
        try:
            # Extract title
            title_element = job_element.query_selector('.jobtitle')
            title = title_element.text_content().strip() if title_element else ""

            # Extract company
            company_element = job_element.query_selector('.companyName')
            company = company_element.text_content().strip() if company_element else ""

            # Extract location
            location_element = job_element.query_selector('.loc')
            location = location_element.text_content().strip() if location_element else ""

            # Extract experience
            exp_element = job_element.query_selector('.exp')
            experience = exp_element.text_content().strip() if exp_element else ""

            # Extract link
            link_element = job_element.query_selector('a')
            link = link_element.get_attribute('href') if link_element else ""
            if link and not link.startswith('http'):
                link = f"{NAUKRI_BASE_URL}{link}"

            job_data = {
                'title': title,
                'company': company,
                'location': location,
                'experience': experience,
                'link': link
            }

            return job_data

        except Exception as e:
            logger.error(f"Error extracting job data: {str(e)}")
            return None