import json
import sys
from pathlib import Path
from typing import Any, Dict

from loguru import logger


def setup_logger(log_path: str = None):
    """Configure loguru logger with custom formatting and optional file output.

    Args:
        log_path (str, optional): Path to log file. If None, logs only to console.
    """
    # Remove default handler
    logger.remove()

    # Format for logs
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    # Add console handler with custom format
    logger.add(sys.stderr, format=log_format, level="DEBUG", colorize=True)

    # Add file handler if log path is provided
    if log_path:
        log_file = Path(log_path)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        logger.add(
            str(log_file),
            format=log_format,
            level="DEBUG",
            rotation="10 MB",  # Rotate when file reaches 10MB
            retention="1 week",  # Keep logs for 1 week
            compression="zip",  # Compress rotated logs
        )

        # Add exception handling
        logger.add(
            str(log_file.parent / "error.log"),
            format=log_format,
            level="ERROR",
            rotation="1 MB",
            retention="1 week",
            compression="zip",
            backtrace=True,
            diagnose=True,
        )

    return logger


def load_workflow_template(template_name: str) -> Dict[str, Any]:
    """Load a workflow template from the templates directory.

    Args:
        template_name: Name of the template file (without .json extension)

    Returns:
        Dict containing the workflow template

    Raises:
        FileNotFoundError: If template doesn't exist
    """
    template_path = Path(__file__).parent / "templates" / "workflows" / f"{template_name}.json"

    if not template_path.exists():
        raise FileNotFoundError(f"Workflow template '{template_name}' not found")

    with open(template_path, "r") as f:
        return json.load(f)
