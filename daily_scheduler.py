#!/usr/bin/env python3
"""
Daily Scheduler for Naukri Agent
Runs resume update at 6:30 AM and 7:00 PM daily
"""

import schedule
import time
from datetime import datetime
from utils.logger import setup_logger
from scheduler import run_resume_only_agent

logger = setup_logger(__name__)


def run_scheduled_task():
    """
    Run the scheduled resume update task
    """
    logger.info(f"🕐 Scheduled task started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        success = run_resume_only_agent()
        if success:
            logger.info("✅ Scheduled resume update completed successfully")
        else:
            logger.error("❌ Scheduled resume update failed")
    except Exception as e:
        logger.error(f"❌ Scheduled task failed with error: {str(e)}")


def start_daily_scheduler():
    """
    Start the daily scheduler that runs at 6:30 AM and 7:00 PM
    """
    logger.info("🚀 Starting Naukri Agent Daily Scheduler")
    logger.info("📅 Schedule: 6:30 AM and 7:00 PM daily")
    logger.info("📄 Task: Resume update only (no job search)")

    # Schedule tasks
    schedule.every().day.at("06:30").do(run_scheduled_task)
    schedule.every().day.at("19:00").do(run_scheduled_task)  # 7:00 PM

    logger.info("⏰ Scheduler started. Waiting for next scheduled run...")

    # Keep the script running
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("🛑 Scheduler stopped by user")
            break
        except Exception as e:
            logger.error(f"❌ Scheduler error: {str(e)}")
            time.sleep(300)  # Wait 5 minutes before retrying


if __name__ == "__main__":
    print("🚀 Naukri Agent Daily Scheduler")
    print("=" * 40)
    print("This will run resume updates at:")
    print("  • 6:30 AM daily")
    print("  • 7:00 PM daily")
    print()
    print("Press Ctrl+C to stop the scheduler")
    print()

    try:
        start_daily_scheduler()
    except KeyboardInterrupt:
        print("\n🛑 Scheduler stopped")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")