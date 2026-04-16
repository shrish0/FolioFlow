# app/core/logger.py
"""Simple analytics logger using Loguru.
Logs are written to a rotating file (logs/analytics.log) and also printed to stdout.
"""

from pathlib import Path
from loguru import logger

# Ensure logs directory exists
LOG_DIR = Path(__file__).resolve().parents[2] / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Configure logger
logger.add(
    LOG_DIR / "analytics.log",
    rotation="10 MB",
    retention="7 days",
    level="INFO",
    enqueue=True,
    backtrace=False,
    diagnose=False,
)

# Export a convenient alias
analytics_logger = logger
