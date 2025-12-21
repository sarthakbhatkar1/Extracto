import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler


class Logger:
    def __init__(self, log_path=None, default_log_path='logs/daemon.log', log_level=logging.INFO):
        """
        Initialize the logger with a.py file handler based on LOG_PATH environment variable.

        Args:
            log_path (str, optional): Path to the log file. Defaults to LOG_PATH env var or default_log_path.
            default_log_path (str): Fallback log file path if LOG_PATH is not set.
            log_level (int): Logging level (e.g., logging.INFO, logging.DEBUG).
        """
        # Determine log file path from environment variable or default
        self.log_path = os.getenv('LOG_PATH', default_log_path) if log_path is None else log_path

        # Ensure the log directory exists
        log_dir = Path(self.log_path).parent
        log_dir.mkdir(parents=True, exist_ok=True)

        # Create logger
        self.logger = logging.getLogger('ExtractoLogger')
        self.logger.setLevel(log_level)

        # Avoid adding multiple handlers if logger is already configured
        if not self.logger.handlers:
            # Create formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

            # Create rotating file handler (max 5MB per file, keep 5 backups)
            file_handler = RotatingFileHandler(
                self.log_path,
                maxBytes=5 * 1024 * 1024,  # 5MB
                backupCount=5
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(log_level)

            # Add handler to logger
            self.logger.addHandler(file_handler)

    def debug(self, message):
        """Log a.py debug message."""
        self.logger.debug(message)

    def info(self, message):
        """Log an info message."""
        self.logger.info(message)

    def warning(self, message):
        """Log a.py warning message."""
        self.logger.warning(message)

    def error(self, message):
        """Log an error message."""
        self.logger.error(message)

    def critical(self, message):
        """Log a.py critical message."""
        self.logger.critical(message)


# Example usage (for testing, can be removed in production)
# if __name__ == "__main__":
#     logger = Logger()
#     logger.info("Logger initialized successfully")
#     logger.debug("This is a.py debug message")
#     logger.error("This is an error message")