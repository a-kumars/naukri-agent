"""
Storage module for Naukri Agent
"""

import os
import pandas as pd
from typing import List, Dict
from utils.logger import setup_logger
from config import JOBS_CSV_PATH

logger = setup_logger(__name__)


class JobStorage:
    """Handles job data storage"""

    def __init__(self, csv_path: str = JOBS_CSV_PATH):
        self.csv_path = csv_path
        self._ensure_csv_exists()

    def _ensure_csv_exists(self):
        """Ensure the CSV file exists with proper headers"""
        if not os.path.exists(self.csv_path):
            os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
            df = pd.DataFrame(columns=['title', 'company', 'location', 'experience', 'link'])
            df.to_csv(self.csv_path, index=False)
            logger.info(f"Created new CSV file: {self.csv_path}")

    def save_jobs(self, jobs: List[Dict]) -> int:
        """
        Save jobs to CSV, avoiding duplicates

        Args:
            jobs: List of job dictionaries

        Returns:
            Number of new jobs saved
        """
        logger.info(f"Attempting to save {len(jobs)} jobs")

        # Read existing jobs
        existing_df = pd.read_csv(self.csv_path)
        existing_links = set(existing_df['link'].dropna())

        # Filter out duplicates
        new_jobs = []
        for job in jobs:
            if job['link'] not in existing_links and job['link']:
                new_jobs.append(job)
                existing_links.add(job['link'])

        if not new_jobs:
            logger.info("No new jobs to save")
            return 0

        # Create DataFrame from new jobs
        new_df = pd.DataFrame(new_jobs)

        # Append to existing CSV
        new_df.to_csv(self.csv_path, mode='a', header=False, index=False)

        logger.info(f"Saved {len(new_jobs)} new jobs to {self.csv_path}")
        return len(new_jobs)

    def get_all_jobs(self) -> pd.DataFrame:
        """
        Get all jobs from CSV

        Returns:
            DataFrame with all jobs
        """
        return pd.read_csv(self.csv_path)

    def get_job_count(self) -> int:
        """
        Get total number of jobs stored

        Returns:
            Number of jobs
        """
        df = self.get_all_jobs()
        return len(df)