"""
=============================================================================
COMMAND CENTER - Task Scheduler
=============================================================================
Schedules and runs automated tasks:
- Daily reports at 9 AM
- Hourly threshold checks
- Weekly summaries on Mondays
=============================================================================
"""

import schedule
import time
import subprocess
import logging
from datetime import datetime
from pathlib import Path
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Path(__file__).parent / 'scheduler.log')
    ]
)
logger = logging.getLogger(__name__)

# Paths
ENGINE_PATH = Path(__file__).parent / "automation_engine.py"
BASE_DIR = Path(__file__).parent.parent.parent

def run_engine(mode: str = "check", period: str = "last_3d"):
    """Run the automation engine"""
    logger.info(f"🚀 Running engine: mode={mode}, period={period}")

    try:
        result = subprocess.run(
            ["python3", str(ENGINE_PATH), f"--mode={mode}", f"--period={period}"],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        if result.returncode == 0:
            logger.info("✅ Engine completed successfully")
            logger.debug(result.stdout)
        else:
            logger.error(f"❌ Engine failed: {result.stderr}")

    except subprocess.TimeoutExpired:
        logger.error("❌ Engine timed out")
    except Exception as e:
        logger.error(f"❌ Error running engine: {e}")

def daily_morning_report():
    """Run at 9 AM - Daily comprehensive report"""
    logger.info("=" * 50)
    logger.info("🌅 DAILY MORNING REPORT")
    logger.info("=" * 50)
    run_engine(mode="report", period="yesterday")

def hourly_threshold_check():
    """Run every hour - Quick threshold check"""
    logger.info("⏰ Hourly threshold check")
    run_engine(mode="check", period="last_3d")

def weekly_summary():
    """Run Monday 10 AM - Weekly summary"""
    logger.info("=" * 50)
    logger.info("📊 WEEKLY SUMMARY")
    logger.info("=" * 50)
    run_engine(mode="report", period="last_7d")

def update_dashboard():
    """Refresh the Streamlit dashboard data"""
    logger.info("🔄 Refreshing dashboard data...")
    # The Streamlit dashboard auto-refreshes, but we can trigger a data update
    run_engine(mode="check", period="last_3d")

def setup_schedule():
    """Configure all scheduled tasks"""
    logger.info("📅 Setting up schedule...")

    # Daily at 9 AM
    schedule.every().day.at("09:00").do(daily_morning_report)
    logger.info("   ✓ Daily report: 09:00")

    # Every hour
    schedule.every().hour.do(hourly_threshold_check)
    logger.info("   ✓ Hourly check: every hour")

    # Monday at 10 AM
    schedule.every().monday.at("10:00").do(weekly_summary)
    logger.info("   ✓ Weekly summary: Monday 10:00")

    # Every 5 minutes - dashboard refresh (optional, more aggressive)
    # schedule.every(5).minutes.do(update_dashboard)

    logger.info("📅 Schedule configured!")

def main():
    """Main scheduler loop"""
    logger.info("=" * 60)
    logger.info("🤖 COMMAND CENTER SCHEDULER")
    logger.info("=" * 60)
    logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Setup schedules
    setup_schedule()

    # Run initial check
    logger.info("\n🔄 Running initial check...")
    run_engine(mode="check", period="last_3d")

    # Start scheduler loop
    logger.info("\n⏳ Entering scheduler loop (Ctrl+C to stop)...")

    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    except KeyboardInterrupt:
        logger.info("\n👋 Scheduler stopped by user")

if __name__ == "__main__":
    main()
