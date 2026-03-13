"""
Main entry point for Naukri Agent
"""

from scheduler import run_agent
from utils.logger import setup_logger

logger = setup_logger(__name__)


def main():
    """Main function"""
    logger.info("Naukri Agent started")

    try:
        success = run_agent()
        if success:
            logger.info("Naukri Agent completed successfully")
        else:
            logger.warning("Naukri Agent completed with warnings")
    except Exception as e:
        logger.error(f"Naukri Agent failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()